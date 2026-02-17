from dataclasses import dataclass
from typing import Optional

@dataclass
class NetworkCredential:
    """
    Representa las credenciales de una red inalámbrica (WiFi).

    Atributos:
        name (str): El nombre (SSID) de la red WiFi.
        password (Optional[str]): La contraseña de la red WiFi en texto claro,
                                  o `None` si no está disponible/recuperable.
        interface (str): El nombre de la interfaz de red a la que pertenece
                         la credencial (ej. "WiFi").
    """
    name: str
    password: Optional[str]
    interface: str
