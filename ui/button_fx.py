import tkinter as tk
from PIL import Image, ImageTk
from typing import Callable, Optional
from utils.resource_utils import resource_path

class ButtonFX:
    """
    Una fábrica para crear botones de Tkinter estilizados y consistentes.
    Encapsula la lógica de apariencia, carga de imagen y efectos para ser reutilizada.
    """
    def __init__(self, config, image_manager):
        """
        Inicializa la fábrica de botones.
        
        Args:
            config (module): El módulo de configuración de la aplicación.
            image_manager (ImageManager): El gestor de imágenes para cargar recursos.
        """
        self.config = config
        self.image_manager = image_manager
        self._load_default_images()

    def _load_default_images(self):
        """Carga las imágenes por defecto para los botones."""
        button_image_path = resource_path('assets/' + self.config.IMAGE_BUTTON)
        self.default_image = self.image_manager.load(
            button_image_path, size=(120, 40), apply_shadow=True,
            shadow_options={'offset': (3, 3), 'shadow_color': (0, 0, 0, 120), 'content_offset_y': 0}
        )
        # Podríamos añadir más variantes aquí si fuera necesario, pero por ahora una es suficiente.

    def create(self, parent: tk.Widget, text: str, command: Callable, enabled_checker: Callable, image: Optional[ImageTk.PhotoImage] = None) -> tk.Button:
        """
        Crea un tk.Button estilizado con efectos de hover y presionado.

        Args:
            parent (tk.Widget): El widget padre para el botón.
            text (str): El texto que se mostrará en el botón.
            command (callable): La función a ejecutar al hacer clic.
            enabled_checker (callable): Una función que devuelve True si el botón debe estar activo.
            image (Optional[ImageTk.PhotoImage]): Una imagen específica para este botón. 
                                                   Si es None, se usa la imagen por defecto.

        Returns:
            tk.Button: La instancia del widget de botón creado y configurado.
        """
        image_to_use = image if image is not None else self.default_image

        def _command_wrapper():
            if enabled_checker():
                command()

        btn = tk.Button(parent, image=image_to_use, text=text, command=_command_wrapper,
                        compound="center",
                        font=(self.config.FONT_FAMILY, self.config.FONT_SIZE_NORMAL, self.config.FONT_WEIGHT_BOLD),
                        fg=self.config.COLOR_TEXT, 
                        bg=self.config.COLOR_BACKGROUND,
                        activebackground=self.config.COLOR_BACKGROUND,
                        activeforeground=self.config.COLOR_ACCENT,
                        cursor="hand2",
                        bd=0, 
                        highlightthickness=0, 
                        borderwidth=0)

        def _on_enter(event):
            if enabled_checker():
                btn.config(fg=self.config.COLOR_ACCENT)

        def _on_leave(event):
            btn.config(fg=self.config.COLOR_TEXT)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)
        
        return btn
