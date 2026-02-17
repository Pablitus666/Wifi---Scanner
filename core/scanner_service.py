from typing import List
from core.interfaces import WiFiProvider
from utils.localization_manager import LocalizationManager
from core.models import NetworkCredential
from core.exceptions import ScannerServiceException, OpenNetworkException, AdminRightsRequiredError, PasswordNotFoundError
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

class WiFiScannerService:
    """
    Servicio de dominio para escanear redes WiFi y obtener sus credenciales.

    Orquesta un proveedor de WiFi (implementación de `WiFiProvider`) para interactuar
    con el sistema operativo y recuperar los perfiles de red y sus contraseñas.
    Utiliza un pool de hilos para obtener contraseñas de manera eficiente y asíncrona.
    """

    def __init__(self, provider: WiFiProvider, localization_manager: LocalizationManager):
        """
        Inicializa el WiFiScannerService con un proveedor de WiFi específico.

        Args:
            provider (WiFiProvider): Una instancia de una clase que implementa
                                     la interfaz `WiFiProvider` (ej. `NetshWifiProvider`).
            localization_manager (LocalizationManager): El gestor para obtener cadenas de texto localizadas.
        """
        self.provider = provider
        self.localization_manager = localization_manager

    def scan(self) -> List[NetworkCredential]:
        """
        Realiza un escaneo de redes WiFi, obtiene todos los perfiles configurados
        y, si es posible, sus contraseñas.
        """
        try:
            profiles = self.provider.list_profiles()
            if not profiles:
                return []

            credentials = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_profile = {executor.submit(self.provider.get_password, profile): profile for profile in profiles}
                
                for future in as_completed(future_to_profile):
                    profile_name = future_to_profile[future]
                    try:
                        password = future.result()
                        credentials.append(
                            NetworkCredential(
                                name=profile_name,
                                password=password, # Contraseña obtenida
                                interface="WiFi"
                            )
                        )
                    except OpenNetworkException:
                        credentials.append(
                            NetworkCredential(
                                name=profile_name,
                                password=self.localization_manager.get_string("status_open_network"),
                                interface="WiFi"
                            )
                        )
                    except (AdminRightsRequiredError, PasswordNotFoundError) as exc:
                        logging.warning(f"No se pudo obtener la contraseña para '{profile_name}': {exc.message}")
                        credentials.append(
                            NetworkCredential(
                                name=profile_name,
                                password=exc.message, # El mensaje ya está localizado desde el provider
                                interface="WiFi"
                            )
                        )
                    except Exception as exc:
                         logging.error(f"Error inesperado al obtener contraseña para '{profile_name}': {exc}", exc_info=True)
                         credentials.append(
                            NetworkCredential(
                                name=profile_name,
                                password=self.localization_manager.get_string("status_general_error"),
                                interface="WiFi"
                            )
                        )
            
            credentials.sort(key=lambda x: x.name)
            return credentials

        except Exception as e:
            raise ScannerServiceException(f"Error al escanear redes: {e}") from e
