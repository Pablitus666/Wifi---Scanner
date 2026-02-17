import pytest
import subprocess
from unittest.mock import MagicMock, patch
from infrastructure.netsh_provider import NetshWifiProvider
from infrastructure.command_executor import CommandExecutor

# Mockear locale.getdefaultlocale para asegurar un idioma consistente durante las pruebas
@pytest.fixture(autouse=True)
def mock_locale_getdefaultlocale():
    with patch('locale.getdefaultlocale', return_value=('es_ES', 'cp1252')):
        yield

@pytest.fixture
def mock_executor():
    return MagicMock(spec=CommandExecutor)

@pytest.fixture
def netsh_provider(mock_executor):
    return NetshWifiProvider(mock_executor)

def test_list_profiles_success(mock_executor, netsh_provider):
    # Simular la salida de netsh wlan show profiles en español
    mock_executor.run.return_value = """

Perfiles en la interfaz "Wi-Fi"

    Perfil de todos los usuarios     : MiRed1
    Perfil de todos los usuarios     : MiRed Espacio
    Perfil de todos los usuarios     : MiRed3
"""
    profiles = netsh_provider.list_profiles()
    assert len(profiles) == 3
    assert "MiRed1" in profiles
    assert "MiRed Espacio" in profiles
    assert "MiRed3" in profiles
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profiles'])

def test_list_profiles_empty(mock_executor, netsh_provider):
    # Simular ninguna red encontrada
    mock_executor.run.return_value = """

Perfiles en la interfaz "Wi-Fi"
    """
    profiles = netsh_provider.list_profiles()
    assert len(profiles) == 0
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profiles'])

def test_list_profiles_called_process_error(mock_executor, netsh_provider):
    # Simular un subprocess.CalledProcessError al ejecutar el comando netsh
    mock_executor.run.side_effect = subprocess.CalledProcessError(1, ['netsh', 'wlan', 'show', 'profiles'])
    profiles = netsh_provider.list_profiles()
    assert len(profiles) == 0
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profiles'])

def test_get_password_success(mock_executor, netsh_provider):
    profile_name = "MiRed1"
    # Simular la salida de netsh wlan show profile name="MiRed1" key=clear en español
    mock_executor.run.return_value = f"""

    Coste                             : ilimitado
    SSID de red                       : MiRed1
    Tipo de red                       : Infraestructura
    Tipo de radio                     : 802.11n
    Modo de autenticación             : WPA2-Personal
    Cifrado                           : CCMP
    Contenido de la clave             : MiContraseñaSecreta123
"""
    password = netsh_provider.get_password(profile_name)
    assert password == "MiContraseñaSecreta123"
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'])

def test_get_password_no_key(mock_executor, netsh_provider):
    profile_name = "RedSinClave"
    # Simular la salida cuando no hay clave (por ejemplo, red abierta o no encontrada)
    mock_executor.run.return_value = f"""

    Coste                             : ilimitado
    SSID de red                       : RedSinClave
    Tipo de red                       : Infraestructura
    Tipo de radio                     : 802.11n
    Modo de autenticación             : Abierto
    Cifrado                           : Ninguno
"""
    password = netsh_provider.get_password(profile_name)
    assert password is None
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'])

def test_get_password_called_process_error(mock_executor, netsh_provider):
    profile_name = "RedErrorPermisos"
    mock_executor.run.side_effect = subprocess.CalledProcessError(1, ['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'])
    password = netsh_provider.get_password(profile_name)
    assert password is None
    mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'])

def test_netsh_provider_locale_en(mock_executor):
    # Probar que el proveedor usa el idioma correcto si se mockea el locale a inglés
    with patch('locale.getdefaultlocale', return_value=('en_US', 'utf8')):
        provider_en = NetshWifiProvider(mock_executor)
        # Simular la salida de netsh wlan show profiles en inglés
        mock_executor.run.return_value = """

Profiles on interface "Wi-Fi"

    All User Profile     : MyNetwork1
    All User Profile     : MyNetwork2
"""
        profiles = provider_en.list_profiles()
        assert len(profiles) == 2
        assert "MyNetwork1" in profiles
        assert "MyNetwork2" in profiles
        mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profiles'])
        mock_executor.run.reset_mock() # Reset mock para la siguiente aserción

        profile_name = "MyNetwork1"
        mock_executor.run.return_value = f"""

    Authentication                      : WPA2-Personal
    Cipher                              : CCMP
    Key Content                         : MySecretPass123
"""
        password = provider_en.get_password(profile_name)
        assert password == "MySecretPass123"
        mock_executor.run.assert_called_once_with(['netsh', 'wlan', 'show', 'profile', f'name="{profile_name}"', 'key=clear'])
