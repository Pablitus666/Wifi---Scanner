import json
import os
import locale
import logging
from typing import Dict, Any, Tuple

class LocalizationManager:
    """
    Gestiona la carga y el acceso a cadenas de texto localizadas para la aplicación.

    Detecta el idioma del sistema operativo y carga el archivo JSON de traducción
    correspondiente. Proporciona un método para obtener cadenas traducidas
    y soporta el formateo de cadenas con argumentos.
    """
    def __init__(self, locales_dir: str, default_lang: str = 'en'):
        """
        Inicializa el LocalizationManager.

        Args:
            locales_dir (str): La ruta al directorio que contiene los archivos JSON de idioma.
            default_lang (str, optional): El código del idioma predeterminado a usar
                                          si el idioma del sistema no se puede detectar
                                          o no hay un archivo de idioma para él.
                                          Defaults to 'en'.
        """
        self.locales_dir = locales_dir
        self.default_lang = default_lang
        self.translations: Dict[str, str] = {}
        self._load_translations()

    def _get_system_language(self) -> str:
        """
        Intenta determinar el código de idioma principal del sistema operativo actual.

        Utiliza `locale.getdefaultlocale()` para obtener la configuración regional
        y extrae el código de idioma de dos letras (ej., 'es' para español, 'en' para inglés).

        Returns:
            str: El código de idioma de dos letras del sistema (ej. 'es', 'en'),
                 o el `default_lang` si no se puede determinar o ocurre un error.
        """
        try:
            # locale.getdefaultlocale() puede devolver una tupla como ('es_ES', 'cp1252')
            system_locale_tuple: Tuple[Optional[str], Optional[str]] = locale.getdefaultlocale()
            if system_locale_tuple and system_locale_tuple[0]:
                lang_code = system_locale_tuple[0].split('_')[0].lower()
                logging.info(f"Idioma del sistema detectado: {lang_code}")
                return lang_code
        except Exception as e:
            logging.warning(f"No se pudo detectar el idioma del sistema: {e}. Usando el idioma predeterminado '{self.default_lang}'.")
        return self.default_lang

    def _load_translations(self):
        """
        Carga las cadenas de traducción desde un archivo JSON.

        Primero intenta cargar el archivo de idioma que coincide con el idioma del sistema.
        Si no se encuentra, intenta cargar el archivo del idioma predeterminado (`default_lang`).
        En caso de errores de lectura o análisis, registra el error y las traducciones
        permanecerán vacías.
        """
        lang = self._get_system_language()
        lang_file_path = os.path.join(self.locales_dir, f"{lang}.json")

        # Verificar si existe el archivo para el idioma detectado.
        if not os.path.exists(lang_file_path):
            logging.warning(f"No se encontró el archivo de idioma '{lang_file_path}'. Intentando cargar el idioma predeterminado '{self.default_lang}'.")
            # Si no existe, intentar con el idioma predeterminado.
            lang_file_path = os.path.join(self.locales_dir, f"{self.default_lang}.json")
            if not os.path.exists(lang_file_path):
                logging.error(f"No se encontró el archivo de idioma predeterminado '{self.default_lang}.json' en '{self.locales_dir}'. Las traducciones no estarán disponibles.")
                return

        try:
            with open(lang_file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            logging.info(f"Traducciones cargadas para el idioma: {lang}")
        except json.JSONDecodeError as e:
            logging.error(f"Error al analizar el archivo de idioma '{lang_file_path}': {e}. Las traducciones no estarán disponibles.")
        except Exception as e:
            logging.error(f"Error inesperado al cargar las traducciones desde '{lang_file_path}': {e}. Las traducciones no estarán disponibles.")

    def get_string(self, key: str, *args: Any, **kwargs: Any) -> str:
        """
        Obtiene una cadena de texto traducida por su clave.

        Si la clave existe, la cadena se devuelve y se formatea con los
        argumentos `*args` y `**kwargs` si se proporcionan. Si la clave no se encuentra,
        se devuelve una cadena indicando la clave faltante para depuración.

        Args:
            key (str): La clave de la cadena de texto a recuperar (ej. "app_name", "scan_button").
            *args (Any): Argumentos posicionales opcionales para formatear la cadena.
            **kwargs (Any): Argumentos de palabra clave opcionales para formatear la cadena.

        Returns:
            str: La cadena de texto traducida y formateada, o un mensaje de error
                 si la clave no se encuentra.
        """
        s = self.translations.get(key, f"MISSING_TRANSLATION: {key}")
        if args or kwargs:
            try:
                s = s.format(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error al formatear la cadena de traducción para la clave '{key}' con args {args} y kwargs {kwargs}: {e}")
        return s
