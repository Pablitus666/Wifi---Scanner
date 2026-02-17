class CoreException(Exception):
    """
    Excepción base para todos los errores dentro de la capa de dominio ('core').

    Sirve como una clase base común para excepciones personalizadas, permitiendo
    capturar todos los errores del dominio de manera uniforme.
    """
    pass

class ScannerServiceException(CoreException):
    """
    Excepción específica para errores que ocurren dentro del `WiFiScannerService`.

    Indica problemas relacionados con el escaneo de redes, la obtención de perfiles
    o la recuperación de contraseñas.
    """
    pass

class ReportServiceException(CoreException):
    """
    Excepción específica para errores que ocurren dentro del `ReportService`.

    Indica problemas relacionados con la generación o formato del contenido
    del reporte.
    """
    pass

class ReportSavingError(ReportServiceException):
    """
    Excepción lanzada cuando ocurre un error al intentar guardar un reporte en un archivo.
    """
    pass

class ProfileNotFoundError(ScannerServiceException):
    """Excepción lanzada cuando un perfil de Wi-Fi específico no se encuentra."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PasswordNotFoundError(ScannerServiceException):
    """Excepción lanzada cuando no se puede obtener la contraseña de un perfil."""
    def __init__(self, profile_name, message):
        self.profile_name = profile_name
        self.message = message
        super().__init__(self.message)

class AdminRightsRequiredError(PasswordNotFoundError):
    """Excepción específica para cuando la obtención de la contraseña falla por falta de privilegios de administrador."""
    pass

class OpenNetworkException(Exception):
    """Excepción utilizada para señalar que una red es abierta y por lo tanto no tiene contraseña.
    No se considera un error, sino un estado.
    """
    def __init__(self, profile_name):
        self.profile_name = profile_name
        super().__init__(f"El perfil '{profile_name}' corresponde a una red abierta.")
