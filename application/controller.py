import platform
import logging
import threading
from typing import List, Optional, Callable
from core.models import NetworkCredential
from core.scanner_service import WiFiScannerService
from core.report_service import ReportService
from core.exceptions import ReportSavingError
from infrastructure.netsh_wifi_provider import NetshWiFiProvider
from infrastructure.command_executor import CommandExecutor
from infrastructure.system_validator import WindowsSystemValidator
from utils.localization_manager import LocalizationManager # Importar el gestor de localización

class Controller:
    """
    Orquesta las operaciones de la aplicación, actuando como un puente
    entre la UI y la lógica de negocio (core/infrastructure).

    Responsabilidades:
    - Inicializar y gestionar los servicios de backend.
    - Manejar la lógica de la aplicación, como iniciar escaneos.
    - Comunicarse con la UI a través de callbacks.
    - Validar la compatibilidad del sistema y los permisos.
    """

    def __init__(self, base_path: str, localization_manager: LocalizationManager):
        """
        Inicializa el Controller.

        Args:
            base_path (str): La ruta base de la aplicación para recursos.
            localization_manager (LocalizationManager): Gestor de internacionalización para cadenas de texto.
        """
        self.base_path = base_path
        self.localization_manager = localization_manager # Guardar la instancia del gestor de localización
        self.is_scanning = False
        # --- Inyección de Dependencias ---
        executor = CommandExecutor()
        self.validator = WindowsSystemValidator()
        wifi_provider = NetshWiFiProvider(executor, self.localization_manager)
        self.scanner_service = WiFiScannerService(wifi_provider, self.localization_manager)
        self.report_service = ReportService(localization_manager) # Pasar localization_manager a ReportService
        logging.info("Controller inicializado.")

    def is_system_compatible(self) -> bool:
        """
        Verifica si el sistema operativo actual es compatible con la aplicación.

        Returns:
            bool: True si el sistema es compatible (Windows), False en caso contrario.
        """
        return self.validator.validate()

    def get_system_info(self) -> str:
        """
        Retorna información básica del sistema operativo (nombre y versión).

        Returns:
            str: Una cadena que describe el sistema operativo.
        """
        return f"{platform.system()} {platform.release()}"

    def start_scan_thread(self, on_success: Callable, on_error: Callable):
        """
        Inicia el proceso de escaneo de redes WiFi en un hilo separado
        para evitar bloquear la interfaz de usuario.

        Verifica los permisos de administrador antes de iniciar el escaneo,
        ya que la obtención de contraseñas requiere privilegios elevados.

        Args:
            on_success (Callable): Callback a ejecutar tras un escaneo exitoso,
                                  recibe una lista de NetworkCredential.
            on_error (Callable): Callback a ejecutar si ocurre un error,
                                 recibe un mensaje de error (str).
        """
        if self.is_scanning:
            return
        
        if not self.validator.is_admin():
            on_error(self.localization_manager.get_string("admin_privileges_required"))
            return

        self.is_scanning = True
        
        thread = threading.Thread(
            target=self._scan_worker,
            args=(on_success, on_error),
            daemon=True
        )
        thread.start()

    def _scan_worker(self, on_success: Callable, on_error: Callable):
        """
        Trabajador de hilo que realiza el escaneo real de las redes WiFi
        y la recuperación de credenciales.

        Gestiona la lógica de llamada al WiFiScannerService y notifica a la UI
        mediante los callbacks proporcionados.

        Args:
            on_success (Callable): Callback para notificar el éxito del escaneo.
            on_error (Callable): Callback para notificar cualquier error durante el escaneo.
        """
        try:
            logging.info(self.localization_manager.get_string("scanning_message_log"))
            credentials = self.scanner_service.scan()
            logging.info(self.localization_manager.get_string("scan_completed_log", len(credentials)))
            on_success(credentials)
        except Exception as e:
            logging.exception(self.localization_manager.get_string("error_occurred_during_scan_log")) # Nueva clave de log
            on_error(self.localization_manager.get_string("error_occurred_during_scan"))
        finally:
            self.is_scanning = False

    def format_credentials_for_display(self, credentials: List[NetworkCredential]) -> str:
        """
        Formatea una lista de credenciales de red para su visualización en la interfaz de usuario.

        Args:
            credentials (List[NetworkCredential]): Lista de objetos NetworkCredential.

        Returns:
            str: Una cadena formateada con los nombres de red y sus contraseñas.
        """
        return self.report_service.format_credentials_to_string(credentials)

    def save_report(self, file_path: str, credentials: List[NetworkCredential]) -> (bool, Optional[str]):
        """
        Orquesta la generación y guardado de un reporte de credenciales WiFi.

        Args:
            file_path (str): La ruta completa donde se guardará el archivo del reporte.
            credentials (List[NetworkCredential]): Lista de credenciales a incluir.

        Returns:
            Tuple[bool, Optional[str]]: (True, None) si tiene éxito, 
                                        (False, error_message) si falla.
        """
        try:
            logging.info(self.localization_manager.get_string("starting_report_save_log", file_path=file_path))
            
            system_info = self.get_system_info()
            content = self.report_service.generate_report_content(credentials, system_info)
            
            self.report_service.save_report_to_file(file_path, content)
            
            logging.info(self.localization_manager.get_string("report_saved_successfully_log"))
            return True, None
        
        except ReportSavingError as e:
            logging.exception(self.localization_manager.get_string("failed_to_save_report_log", file_path=file_path))
            return False, str(e)
            
        except Exception as e:
            logging.exception(self.localization_manager.get_string("failed_to_save_report_log", file_path=file_path))
            return False, self.localization_manager.get_string("failed_to_save_report")

