# wifi_scanner/infrastructure/windows_system_validator.py
import platform
import ctypes
from core.interfaces import SystemValidator
from core.exceptions import SystemCompatibilityError
from ui.i18n import i18n # Importar i18n aquí

class WindowsSystemValidator(SystemValidator):
    """
    Implementación concreta de SystemValidator para sistemas operativos Windows.
    Verifica la compatibilidad y si la aplicación se ejecuta con privilegios de administrador.
    """
    def __init__(self):
        self._is_admin = self._check_admin_status()

    def _check_admin_status(self) -> bool:
        """
        Verifica si el proceso actual tiene privilegios de administrador.
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            # Si no es Windows (por ejemplo, durante pruebas en otro OS)
            return False

    def is_compatible(self) -> bool:
        """
        Verifica si el sistema operativo es Windows.
        """
        return platform.system() == "Windows"

    def get_compatibility_message(self) -> str:
        """
        Retorna un mensaje de compatibilidad.
        """
        if self.is_compatible():
            if self._is_admin:
                return i18n.get_text("system_compatible_admin")
            else:
                return i18n.get_text("system_compatible_no_admin")
        else:
            return i18n.get_text("system_not_compatible", os_name=platform.system())

    def is_admin(self) -> bool:
        """
        Retorna True si la aplicación se está ejecutando como administrador, False en caso contrario.
        """
        return self._is_admin
