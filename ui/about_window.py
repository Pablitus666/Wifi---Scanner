import os
import tkinter as tk
from PIL import Image, ImageTk
from utils.localization_manager import LocalizationManager
import config
from utils.resource_utils import resource_path
from ui.button_fx import ButtonFX

class AboutWindow(tk.Toplevel):
    """
    Ventana emergente que muestra información "Acerca de" la aplicación.
    """
    def __init__(self, parent, config_module, image_manager, localization_manager: LocalizationManager, button_factory: ButtonFX):
        """
        Inicializa la ventana "Acerca de".
        """
        super().__init__(parent)
        self.config = config_module
        self.image_manager = image_manager
        self.localization_manager = localization_manager
        self.button_factory = button_factory

        self.title(self.localization_manager.get_string("about_title"))
        self.configure(bg=self.config.COLOR_BACKGROUND)
        self.resizable(False, False)
        
        icon_path = resource_path(os.path.join('assets', self.config.ICON_LOGO))
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except tk.TclError:
                pass

        self.withdraw()
        self.attributes("-alpha", 0)
        self.transient(parent)

        self._create_widgets()
        
        def _finish_setup():
            w = 370
            h = 200
            x = (self.winfo_screenwidth() // 2) - (w // 2)
            y = (self.winfo_screenheight() // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
            
            self.attributes("-alpha", 1)
            self.deiconify()
            self.grab_set()

        self.after(50, _finish_setup)

    def _create_widgets(self):
        """
        Crea y organiza los widgets dentro de la ventana "Acerca de".
        """
        frame = tk.Frame(self, bg=self.config.COLOR_BACKGROUND)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        robot_path = resource_path(os.path.join('assets', self.config.IMAGE_ROBOT))
        robot_photo = self.image_manager.load(robot_path, size=(150, 150))
        
        if robot_photo:
            img_label = tk.Label(frame, image=robot_photo, bg=self.config.COLOR_BACKGROUND, bd=0, highlightthickness=0)
            img_label.image = robot_photo # Keep a reference
            img_label.grid(row=0, column=0, rowspan=3, padx=(0, 10), pady=5, sticky="nsew")

        message = tk.Label(
            frame,
            text=self.localization_manager.get_string("about_text"),
            justify="center",
            bg=self.config.COLOR_BACKGROUND,
            fg=self.config.COLOR_TEXT,
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZE_LARGE, "bold"),
            anchor="center",
            wraplength=170
        )
        message.grid(row=0, column=1, rowspan=2, padx=(0, 25), pady=(10, 10), sticky="nsew")

        button_path = resource_path(os.path.join('assets', self.config.IMAGE_BUTTON))
        boton_photo = self.image_manager.load(
            button_path, 
            size=(120, 45),
            apply_shadow=True,
            shadow_options={'offset': (3, 3), 'shadow_color': (0, 0, 0, 90)}
        )
        
        if boton_photo:
            btn_cerrar = self.button_factory.create(
                parent=frame,
                text=self.localization_manager.get_string("close_button"),
                command=self.destroy,
                image=boton_photo,
                enabled_checker=lambda: True # Este botón siempre está habilitado
            )
            btn_cerrar.grid(row=2, column=1, padx=(0, 10), pady=(5, 5), sticky="s")
