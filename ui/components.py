import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import os
from PIL import Image, ImageTk
import logging # Importar logging

from config import IMAGES_DIR # Importamos de config

logger = logging.getLogger(__name__) # Crear instancia de logger

class CustomButton(tk.Button):
    """
    Un botón personalizado que puede incluir una imagen de fondo y texto centrado.
    Replica el comportamiento del botón del script original.
    """
    def __init__(self, master, text: str, command: Callable, image_filename: str = "boton.png", **kwargs):
        self._image_path = os.path.join(IMAGES_DIR, image_filename)
        self._button_image = None
        self._text_color = "white"
        self._active_text_color = "#ffdd57" # Color de texto al pasar el ratón

        # Cargar y redimensionar la imagen para el botón si existe
        if os.path.exists(self._image_path):
            try:
                img = Image.open(self._image_path)
                # El script original usa 100x40. Lo replicamos.
                img = img.resize((100, 40), Image.Resampling.LANCZOS)
                self._button_image = ImageTk.PhotoImage(img)
                logger.info(f"Imagen '{image_filename}' cargada exitosamente desde: {self._image_path}")
            except Exception as e:
                logger.error(f"Error al cargar imagen '{image_filename}' desde '{self._image_path}' para botón: {e}")
                self._button_image = None
        else:
            logger.warning(f"Imagen de botón '{image_filename}' no encontrada en '{self._image_path}'. El botón no tendrá imagen.")
        
        super().__init__(
            master,
            image=self._button_image, # Establece la imagen
            text=text,
            compound="center", # Centra el texto sobre la imagen
            fg=self._text_color, # Color de texto por defecto
            font=("Comic Sans MS", 10, "bold"), # Fuente del script original
            bd=0, # Sin borde
            highlightthickness=0, # Elimina el "paca azul" de enfoque
            bg='#033077', # Color de fondo del botón (del original)
            activebackground='#023047', # Color de fondo cuando está activo (del original)
            activeforeground=self._active_text_color, # Color del texto activo
            command=command,
            **kwargs
        )
        
        # Guardar la referencia a la imagen para evitar que sea eliminada por el recolector de basura
        self.image = self._button_image
        
        # Binds para el efecto hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.config(fg=self._active_text_color)

    def _on_leave(self, event):
        self.config(fg=self._text_color)

# class CustomMessageBox(tk.Toplevel):
#     """
#     Mensajes personalizados con diseño consistente.
#     """
#     def __init__(self, parent, title, message, message_type="info"):
#         super().__init__(parent)
#         ...

