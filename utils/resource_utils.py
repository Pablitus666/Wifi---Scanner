import sys
import os

def resource_path(relative_path):
    """
    Determina la ruta absoluta de un recurso, útil para entornos de desarrollo
    y aplicaciones empaquetadas con PyInstaller.
    """
    if hasattr(sys, 'frozen') and getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
