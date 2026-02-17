from abc import ABC, abstractmethod
from .models import NetworkCredential

class WiFiProvider(ABC):
    """
    Interfaz abstracta (ABC) que define el contrato para cualquier proveedor
    que sea capaz de interactuar con el sistema operativo para obtener
    información sobre las redes WiFi y sus credenciales.

    Las implementaciones concretas de esta interfaz se encargarán de los
    detalles específicos de la plataforma (ej. `netsh` en Windows).
    """

    @abstractmethod
    def list_profiles(self) -> list[str]:
        """
        Retorna una lista de los nombres de todos los perfiles WiFi
        configurados en el sistema.

        Returns:
            list[str]: Una lista de cadenas, donde cada cadena es el nombre
                       de un perfil WiFi.
        """
        pass

    @abstractmethod
    def get_password(self, profile: str) -> str | None:
        """
        Intenta obtener la contraseña en texto claro para un perfil WiFi específico.

        Nota: La obtención de contraseñas suele requerir privilegios elevados
        (ej. permisos de administrador).

        Args:
            profile (str): El nombre del perfil WiFi para el cual se desea la contraseña.

        Returns:
            str | None: La contraseña en texto claro si se encuentra y se puede acceder,
                        o `None` si la contraseña no está disponible, el perfil no existe,
                        o no hay permisos suficientes.
        """
        pass

class SystemValidator(ABC):
    """
    Interfaz abstracta (ABC) que define el contrato para cualquier validador
    de sistema.

    Las implementaciones concretas de esta interfaz se encargarán de verificar
    la compatibilidad del entorno de ejecución de la aplicación.
    """

    @abstractmethod
    def validate(self) -> bool:
        """
        Verifica la compatibilidad del sistema con los requisitos de la aplicación.

        Returns:
            bool: True si el sistema cumple con los requisitos, False en caso contrario.
        """
        pass
