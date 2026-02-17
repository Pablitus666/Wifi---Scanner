# wifi_scanner/infrastructure/netsh_wifi_provider.py
import re
import subprocess
import logging
from typing import List, Optional, Dict
from core.interfaces import WiFiProvider
from utils.localization_manager import LocalizationManager
from core.exceptions import ProfileNotFoundError, PasswordNotFoundError, AdminRightsRequiredError, OpenNetworkException
from infrastructure.command_executor import CommandExecutor

# Language-agnostic keys for parsing netsh output.
# This dictionary can be expanded to support more languages.
NETSH_KEYS: Dict[str, List[str]] = {
    "profile_not_found": ["is not found", "no se encuentra"],
    "key_content": ["Key Content", "Contenido de la clave"],
    "security_key": ["Security key", "Clave de seguridad"],
    "security_key_absent": ["Absent", "Ausente"],
    "authentication": ["Authentication", "Autenticación"],
    "auth_open": ["Open", "Abierta"],
}

class NetshWiFiProvider(WiFiProvider):
    """
    Implementation of WiFiProvider for Windows systems using 'netsh wlan'.
    Refactored for improved language agnosticism.
    """

    def __init__(self, command_executor: CommandExecutor, localization_manager: LocalizationManager):
        self.command_executor = command_executor
        self.localization_manager = localization_manager
        self._interface_name = "Wi-Fi"

    def get_interface_name(self) -> str:
        """Returns the name of the interface this provider manages."""
        return self._interface_name

    def list_profiles(self) -> List[str]:
        """
        Lists the names of available Wi-Fi network profiles on Windows using 'netsh wlan'.
        This method uses string parsing for robustness across different Windows versions
        and language settings, focusing on known indicators for user profiles.
        """
        output = self.command_executor.run(["netsh", "wlan", "show", "profiles"])
        profiles = []
        # Regex to find lines that contain "All User Profile" or "Todos los perfiles de usuario"
        # and capture the profile name after the colon.
        # It's made case-insensitive to handle variations.
        profile_regex = re.compile(r".*(?:All User Profile|Todos los perfiles de usuario|Perfil de todos los usuarios)\s*:\s*(.*)", re.IGNORECASE)
        for line in output.splitlines():
            match = profile_regex.search(line)
            if match:
                profile_name = match.group(1).strip()
                if profile_name:
                    profiles.append(profile_name)
        return profiles

    def _parse_netsh_output(self, output: str) -> Dict[str, str]:
        """Parses colon-separated key-value output from netsh into a dictionary."""
        parsed_data = {}
        for line in output.splitlines():
            match = re.match(r"\s*(.*?)\s*:\s*(.*)", line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                parsed_data[key] = value
        return parsed_data

    def get_password(self, profile: str) -> Optional[str]:
        """
        Gets the password for a specific Wi-Fi network profile on Windows.
        Requires admin privileges for WPA/WPA2 keys.
        Handles cases where the profile does not exist.
        """
        logger = logging.getLogger(__name__)
        try:
            output = self.command_executor.run(["netsh", "wlan", "show", "profile", profile, "key=clear"])
        except subprocess.CalledProcessError as e:
            if any(msg in e.stdout.lower() for msg in NETSH_KEYS["profile_not_found"]):
                logger.info(f"Profile '{profile}' not found, as expected for non-saved networks.")
            else:
                logger.warning(f"Command failed for profile '{profile}': {e.stdout.strip()}")
            return None

        # Parse the entire output into a dictionary
        details = self._parse_netsh_output(output)

        # Look for the password using known keys for different languages
        for key in NETSH_KEYS["key_content"]:
            if key in details:
                return details[key]

        # If no password found, determine the reason
        # Check if security is absent (open network)
        for key in NETSH_KEYS["security_key"]:
            if key in details and any(val in details[key] for val in NETSH_KEYS["security_key_absent"]):
                raise OpenNetworkException(profile)

        # Fallback to checking for "Open" authentication type
        auth_type_key = next((key for key in NETSH_KEYS["authentication"] if key in details), None)
        if auth_type_key:
            auth_type = details[auth_type_key]
            if any(val in auth_type for val in NETSH_KEYS["auth_open"]):
                raise OpenNetworkException(profile)

        # If we are here, the network has security, but the key was not found.
        # This is highly likely due to a lack of administrator privileges.
        raise AdminRightsRequiredError(profile, self.localization_manager.get_string("error_password_not_found_admin_required", profile_name=profile))
