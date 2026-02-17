import tkinter as tk
import os
from typing import Callable, Optional
from utils.localization_manager import LocalizationManager
from utils.resource_utils import resource_path
from ui.button_fx import ButtonFX

class CustomDialog(tk.Toplevel):
    """
    Clase base abstracta para diálogos modales personalizados en Tkinter.
    """
    def __init__(self, parent: tk.Tk | tk.Toplevel, title_key: str, config, localization_manager: LocalizationManager):
        """
        Inicializa una nueva instancia de CustomDialog.
        """
        super().__init__(parent)
        self.config = config
        self.localization_manager = localization_manager

        self.withdraw()
        self.title(self.localization_manager.get_string(title_key))
        self.configure(bg=self.config.COLOR_BACKGROUND)
        self.resizable(False, False)
        self.transient(parent)

        try:
            icon_path = resource_path('assets/' + self.config.ICON_LOGO)
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except tk.TclError:
            print(f"Advertencia: No se pudo cargar el icono de la ventana de diálogo: {icon_path}")
            pass

    def show(self):
        """
        Finaliza la configuración de la ventana, la muestra y la hace modal.
        """
        self.update_idletasks()
        self._center_window()
        self.deiconify()
        self.grab_set()
        self.wait_window(self)

    def _center_window(self):
        """
        Centra la ventana del diálogo respecto a su ventana padre.
        """
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class MessageDialog(CustomDialog):
    """
    Un cuadro de diálogo modal simple para mostrar un mensaje con un botón de "Aceptar".
    """
    def __init__(self, parent: tk.Tk | tk.Toplevel, title_key: str, message_key: Optional[str], config, button_factory: ButtonFX, localization_manager: LocalizationManager, raw_message: Optional[str] = None, *message_args):
        """
        Inicializa una nueva instancia de MessageDialog.
        """
        super().__init__(parent, title_key, config, localization_manager)
        
        self._create_widgets(message_key, button_factory, raw_message, message_args)
        self.show()

    def _create_widgets(self, message_key: Optional[str], button_factory: ButtonFX, raw_message: Optional[str], message_args: tuple):
        """
        Crea los widgets específicos para el MessageDialog.
        """
        main_frame = tk.Frame(self, bg=self.config.COLOR_BACKGROUND, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        if raw_message is not None:
            message_text = raw_message
        elif message_key is not None:
            message_text = self.localization_manager.get_string(message_key, *message_args)
        else:
            message_text = ""

        lbl_message = tk.Label(
            main_frame,
            text=message_text,
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZE_NORMAL),
            bg=self.config.COLOR_BACKGROUND,
            fg=self.config.COLOR_TEXT,
            justify="center",
            wraplength=300
        )
        lbl_message.pack(pady=(0, 20))

        button_frame = tk.Frame(main_frame, bg=self.config.COLOR_BACKGROUND)
        button_frame.pack()

        btn_ok = button_factory.create(button_frame, self.localization_manager.get_string("ok_button"), self.destroy, enabled_checker=lambda: True)
        btn_ok.pack()


class ConfirmationDialog(CustomDialog):
    """
    Un cuadro de diálogo modal para solicitar confirmación con botones "Sí" y "No".
    """
    def __init__(self, parent: tk.Tk | tk.Toplevel, title_key: str, message_key: Optional[str], config, button_factory: ButtonFX, localization_manager: LocalizationManager, raw_message: Optional[str] = None, *message_args):
        """
        Inicializa una nueva instancia de ConfirmationDialog.
        """
        super().__init__(parent, title_key, config, localization_manager)
        self.result = False

        self._create_widgets(message_key, button_factory, raw_message, message_args)
        self.show()

    def _create_widgets(self, message_key: Optional[str], button_factory: ButtonFX, raw_message: Optional[str], message_args: tuple):
        """
        Crea los widgets específicos para el ConfirmationDialog.
        """
        main_frame = tk.Frame(self, bg=self.config.COLOR_BACKGROUND, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        if raw_message is not None:
            message_text = raw_message
        elif message_key is not None:
            message_text = self.localization_manager.get_string(message_key, *message_args)
        else:
            message_text = ""

        lbl_message = tk.Label(
            main_frame,
            text=message_text,
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZE_NORMAL),
            bg=self.config.COLOR_BACKGROUND,
            fg=self.config.COLOR_TEXT,
            justify="center",
            wraplength=300
        )
        lbl_message.pack(pady=(0, 20))

        button_frame = tk.Frame(main_frame, bg=self.config.COLOR_BACKGROUND)
        button_frame.pack()

        enabled_checker = lambda: True
        btn_yes = button_factory.create(button_frame, self.localization_manager.get_string("yes_button"), self._on_yes, enabled_checker)
        btn_no = button_factory.create(button_frame, self.localization_manager.get_string("no_button"), self._on_no, enabled_checker)
        
        btn_yes.pack(side="left", padx=10)
        btn_no.pack(side="left", padx=10)
        
    def _on_yes(self):
        """
        Establece el resultado como True y cierra el diálogo.
        """
        self.result = True
        self.destroy()

    def _on_no(self):
        """
        Establece el resultado como False y cierra el diálogo.
        """
        self.result = False
        self.destroy()
