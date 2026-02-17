import subprocess
import logging

class CommandExecutor:
    """
    Clase de utilidad para ejecutar comandos del sistema operativo.

    Proporciona un método para ejecutar comandos externos de forma controlada,
    especialmente útil en entornos gráficos (GUI) de Windows, donde se busca
    ocultar la ventana de la consola que normalmente aparecería.
    """

    def run(self, command: list[str]) -> str:
        """
        Ejecuta un comando del sistema operativo y captura su salida estándar.

        Este método está configurado para ocultar la ventana de la consola
        en sistemas Windows, proporcionando una experiencia de usuario más limpia.

        Args:
            command (list[str]): El comando a ejecutar, representado como una lista de
                                 cadenas (ej. `['netsh', 'wlan', 'show', 'profiles']`).
                                 El primer elemento es el ejecutable y los subsiguientes
                                 son sus argumentos.

        Returns:
            str: La salida estándar completa del comando ejecutado, decodificada
                 usando UTF-8.

        Raises:
            subprocess.CalledProcessError: Si el comando retorna un código de salida
                                           distinto de cero (indicando un error).
                                           La excepción contendrá información sobre
                                           el código de retorno y la salida/error del comando.
        """
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE

        try:
            result = subprocess.run(
                command,
                capture_output=True, # Capturar tanto stdout como stderr
                text=True,           # Decodificar stdout/stderr como texto
                encoding='utf-8',
                errors='ignore',
                check=True,          # Lanzar CalledProcessError si el código de salida no es cero
                startupinfo=si
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # Re-lanzar la excepción para que el llamador (que tiene el contexto)
            # decida cómo manejarla y si debe ser loggeada como un error.
            raise
