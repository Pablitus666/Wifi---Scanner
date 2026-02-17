import platform
import ctypes
from core.interfaces import SystemValidator

class WindowsSystemValidator(SystemValidator):
    """
    Implementación concreta de la interfaz `SystemValidator` para el sistema operativo Windows.

    Esta clase proporciona métodos para verificar si el entorno de ejecución es Windows
    y si la aplicación se está ejecutando con privilegios de administrador, lo cual
    es crucial para operaciones como la recuperación de contraseñas WiFi.
    """
    def validate(self) -> bool:
        """
        Verifica si el sistema operativo actual es Windows.

        Returns:
            bool: True si el sistema es Windows (independientemente de la versión),
                  False en caso contrario.
        """
        return platform.system().lower() == "windows"

    def is_admin(self) -> bool:
        """
        Verifica si el proceso actual tiene privilegios de administrador.

        Este método es específico de Windows y utiliza la API de `shell32`.

        Returns:
            bool: True si el proceso se ejecuta con privilegios de administrador,
                  False en caso contrario o si ocurre un error (ej. no es Windows).
        """
        try:
            # Solo funciona en Windows. ctypes.windll.shell32 no existirá en otros OS.
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            # Si ctypes falla por alguna razón (ej. no es Windows o DLL no disponible),
            # asumimos que no tiene privilegios de administrador.
            return False
