import tkinter as tk
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from ui.gui import GUI
from application.controller import Controller
import config
from utils.localization_manager import LocalizationManager
from utils.resource_utils import resource_path # Import resource_path from the new utility module
import ctypes # Import ctypes

def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, config.LOG_FILE)

    # Configuración básica del logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file_path,
                maxBytes=config.LOG_MAX_BYTES,
                backupCount=config.LOG_BACKUP_COUNT,
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)  # También muestra logs en consola
        ]
    )
    logging.info("Configuración de logging completada.")


if __name__ == "__main__":
    # --- Punto de Entrada de la Aplicación ---
    
    # Set DPI awareness for Windows
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per Monitor V2
    except AttributeError:
        # Not running on Windows or shcore is not available
        pass

    # 0. Configurar logging
    log_dir = resource_path('logs') # Usa resource_path para la carpeta de logs
    setup_logging(log_dir)

    # 1. Configurar internacionalización
    locales_dir = resource_path('assets/locales') # Usa resource_path para la carpeta de locales
    localization_manager = LocalizationManager(locales_dir)

    # 2. Crear el controlador
    app_controller = Controller(resource_path(''), localization_manager) # Pasa la ruta base si el controlador la necesita
    
    # 3. Crear la ventana principal de Tkinter
    root = tk.Tk()
    
    # 4. Crear la GUI, inyectando el controlador y el gestor de localización
    app = GUI(root, app_controller, localization_manager)
    
    # 5. Iniciar el bucle principal de la aplicación
    root.mainloop()
