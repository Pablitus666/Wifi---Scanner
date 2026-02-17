import re
import locale
import subprocess
from typing import List, Optional
from core.interfaces import WiFiProvider
from .command_executor import CommandExecutor

class NetshWifiProvider(WiFiProvider):
    """
    Implementación concreta de la interfaz `WiFiProvider` para sistemas operativos Windows.

    Esta clase utiliza la utilidad de línea de comandos `netsh wlan` para interactuar
    con las configuraciones de red inalámbrica del sistema, permitiendo listar perfiles
    WiFi y, si los permisos lo permiten, obtener sus contraseñas.

    Soporta la internacionalización de la salida de `netsh` mediante expresiones regulares
    localizadas, lo que la hace más robusta en diferentes versiones de idioma de Windows.
    """

    def __init__(self, executor: CommandExecutor):
        """
        Inicializa el NetshWifiProvider.

        Args:
            executor (CommandExecutor): Una instancia de `CommandExecutor` para ejecutar
                                       comandos del sistema de forma oculta.
        """
        self.executor = executor
        self.profile_regex: re.Pattern = None # Inicializado en _set_localized_regexes
        self.key_regex: re.Pattern = None      # Inicializado en _set_localized_regexes
        self._set_localized_regexes()

    def _set_localized_regexes(self):
        """
        Determina la configuración regional del sistema y establece las expresiones
        regulares apropiadas para el análisis de la salida de `netsh`.

        Este método se ejecuta durante la inicialización para adaptar el análisis
        a las cadenas de texto esperadas en el idioma del sistema operativo,
        como "Perfil de todos los usuarios" o "Key Content".
        """
        system_locale_tuple = locale.getdefaultlocale()
        lang_code = 'en' # Idioma por defecto
        if system_locale_tuple and system_locale_tuple[0]:
            lang_code = system_locale_tuple[0].split('_')[0].lower()

        # Diccionario de cadenas localizadas para los patrones regex
        localized_strings = {
            'en': {
                'profile_prefix': r"All User Profile",
                'key_content_prefix': r"Key Content"
            },
            'es': {
                'profile_prefix': r"Perfil de todos los usuarios",
                'key_content_prefix': r"Contenido de la clave"
            },
            'fr': {
                'profile_prefix': r"Profil de tous les utilisateurs",
                'key_content_prefix': r"Contenu de la clé"
            },
            'de': {
                'profile_prefix': r"Benutzerprofil",
                'key_content_prefix': r"Schlüsselinhalt"
            },
            'it': {
                'profile_prefix': r"Profilo di tutti gli utenti",
                'key_content_prefix': r"Contenuto chiave"
            },
            'pt': {
                'profile_prefix': r"Perfil de todos os usuários",
                'key_content_prefix': r"Conteúdo da chave"
            }
        }

        # Obtener los prefijos para el idioma actual o usar inglés como fallback
        current_lang_strings = localized_strings.get(lang_code, localized_strings['en'])
        profile_prefix = current_lang_strings['profile_prefix']
        key_content_prefix = current_lang_strings['key_content_prefix']
        
        # Compilar las expresiones regulares para un uso eficiente
        self.profile_regex = re.compile(rf"{profile_prefix}\s*:\s*(.*)")
        self.key_regex = re.compile(rf"{key_content_prefix}\s*:\s*(.*)")

    def list_profiles(self) -> List[str]:
        """
        Obtiene una lista de los nombres de los perfiles WiFi configurados
        en el sistema Windows utilizando el comando `netsh wlan show profiles`.

        Returns:
            List[str]: Una lista de cadenas, donde cada cadena es el nombre
                       de un perfil WiFi. Retorna una lista vacía si no se
                       encuentran perfiles o si ocurre un error al ejecutar el comando.
        
        Raises:
            Nada: Los errores de ejecución de comandos se capturan internamente
                  y se manejan devolviendo una lista vacía.
        """
        try:
            output = self.executor.run(['netsh', 'wlan', 'show', 'profiles'])
            return self.profile_regex.findall(output)
        except subprocess.CalledProcessError:
            # Esto puede ocurrir si netsh no está disponible o hay un problema de permisos.
            # No elevamos la excepción aquí, solo devolvemos una lista vacía.
            return []
        except Exception:
            # Para cualquier otra excepción inesperada
            return []

    def get_password(self, profile: str) -> Optional[str]:
        """
        Intenta obtener la contraseña en texto claro para un perfil WiFi específico
        utilizando el comando `netsh wlan show profile name="<profile>" key=clear`.

        Esta operación generalmente requiere privilegios de administrador.

        Args:
            profile (str): El nombre del perfil WiFi para el cual se desea la contraseña.

        Returns:
            Optional[str]: La contraseña en texto claro si se encuentra y se puede acceder.
                           Retorna `None` si la contraseña no está disponible, el perfil no existe,
                           no hay permisos suficientes (ej. no se ejecuta como administrador),
                           o si ocurre un error al ejecutar el comando.
        
        Raises:
            Nada: Los errores de ejecución de comandos se capturan internamente
                  y se manejan devolviendo `None`.
        """
        try:
            # El perfil puede contener caracteres especiales, necesita comillas
            command = ['netsh', 'wlan', 'show', 'profile', f'name="{profile}"', 'key=clear']
            output = self.executor.run(command)
            
            match = self.key_regex.search(output)
            if match:
                return match.group(1).strip()
            return None
        except subprocess.CalledProcessError:
            # Esto puede ocurrir si el usuario no tiene permisos de administrador,
            # o si el perfil no existe o no tiene una clave clara.
            return None
        except Exception:
            # Para cualquier otra excepción inesperada
            return None
