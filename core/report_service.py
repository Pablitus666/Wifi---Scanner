from datetime import datetime
import getpass
from typing import List
from core.models import NetworkCredential
from utils.localization_manager import LocalizationManager
from core.exceptions import ReportSavingError

class ReportService:
    """
    Servicio de dominio encargado de la generación y formato de contenidos
    para los reportes de credenciales WiFi.
    Centraliza la lógica de cómo se estructura la información en el reporte,
    incluyendo detalles del sistema y la lista de redes/contraseñas.
    """
    def __init__(self, localization_manager: LocalizationManager):
        """
        Inicializa el ReportService con una instancia del gestor de localización.
        Args:
            localization_manager (LocalizationManager): Gestor de internacionalización para cadenas de texto.
        """
        self.localization_manager = localization_manager

    def save_report_to_file(self, file_path: str, content: str):
        """
        Guarda el contenido del reporte en un archivo de texto.

        Args:
            file_path (str): La ruta completa donde se guardará el archivo.
            content (str): El contenido del reporte a escribir.

        Raises:
            ReportSavingError: Si ocurre un error de E/S durante el guardado.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
        except IOError as e:
            raise ReportSavingError(
                self.localization_manager.get_string("failed_to_save_report_io_error", file_path=file_path)
            ) from e

    def format_credentials_to_string(self, credentials: List[NetworkCredential]) -> str:
        """
        Convierte una lista de objetos NetworkCredential en una cadena de texto
        simple, donde cada credencial se representa en una línea separada con
        el formato "NombreRed = Contraseña".
        Args:
            credentials (List[NetworkCredential]): Lista de credenciales de red a formatear.
        Returns:
            str: Una cadena de texto con todas las credenciales formateadas,
                 o una cadena vacía si la lista de credenciales está vacía.
        """
        if not credentials:
            return ""
        return "".join([f"{cred.name} = {cred.password}\n" for cred in credentials])

    def generate_report_content(self, credentials: List[NetworkCredential], system_info: str) -> str:
        """
        Genera el contenido completo de un reporte de credenciales WiFi en formato de texto.
        El reporte incluye un banner ASCII, información de fecha, usuario y sistema,
        seguido de la lista de redes y contraseñas obtenidas.
        Args:
            credentials (List[NetworkCredential]): La lista de objetos NetworkCredential
                                                 a incluir en la sección principal del reporte.
            system_info (str): Una cadena que contiene información sobre el sistema operativo
                               donde se ejecutó el escaneo.
        Returns:
            str: El contenido completo del reporte como una cadena de texto lista para ser guardada.
        """
        
        BANNER_ASCII = r"""_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
     ____       _     _ _ _                   
    |  _ \ __ _| |__ | (_) |_ _   _ ___       
    | |_) / _` | '_ \| | | __| | | / __|      
    |  __/ (_| | |_) | | | |_| |_| \__ \_ _ _ 
    |_|   \__,_|_.__/|_|_|\__|\__,_|___(_|_|_)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

"""
        report_lines = []
        report_lines.append(BANNER_ASCII)
        report_lines.append(f"{self.localization_manager.get_string('report_date_prefix')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append(f"{self.localization_manager.get_string('report_user_prefix')}: {getpass.getuser()}\n")
        report_lines.append(f"{self.localization_manager.get_string('report_system_prefix')}: {system_info}\n\n")
        report_lines.append(f"{self.localization_manager.get_string('report_networks_header')}:\n\n")
        # Usar el nuevo método de formato
        report_lines.append(self.format_credentials_to_string(credentials))
        report_lines.append("\n" + "-" * 50 + "\n")
        report_lines.append(f"{self.localization_manager.get_string('report_generated_by')}\n")
        return "".join(report_lines)
