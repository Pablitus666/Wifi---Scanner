import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel, PhotoImage
from PIL import Image, ImageTk
from typing import List, Optional, Callable

import config
from ui.about_window import AboutWindow
from ui.image_utils import ImageManager
from core.models import NetworkCredential
from ui.dialogs import ConfirmationDialog, MessageDialog
from utils.localization_manager import LocalizationManager
from utils.resource_utils import resource_path
from ui.button_fx import ButtonFX

class GUI:
    """
    Clase principal que gestiona la Interfaz Gráfica de Usuario (GUI) de la aplicación.
    """
    def __init__(self, root: tk.Tk, controller, localization_manager: LocalizationManager):
        """
        Inicializa la GUI de la aplicación.
        """
        self.root = root
        self.controller = controller
        self.localization_manager = localization_manager
        self.app_state = AppState()
        self.image_manager = ImageManager()
        self.button_factory = ButtonFX(config, self.image_manager)
        
        self.setup_window()
        self.setup_widgets()
        
        self.buttons_enabled = True
        
        self.root.after(200, self.start_scan)

    def setup_window(self):
        """
        Configura la ventana principal de la aplicación.
        """
        self.root.withdraw()
        self.root.title(self.localization_manager.get_string("app_name"))
        self.root.config(bg=config.COLOR_BACKGROUND)
        try:
            icon_path = resource_path('assets/' + config.ICON_LOGO)
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except tk.TclError:
            pass
        self.root.resizable(0, 0)
        self.centrar_ventana(self.root, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.root.deiconify()

    def setup_widgets(self):
        """
        Configura y organiza todos los widgets principales.
        """
        text_box_frame = tk.Frame(self.root, bg=config.COLOR_BACKGROUND, padx=10)
        text_box_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 6))

        self.text_box = scrolledtext.ScrolledText(
            text_box_frame, width=48, height=8,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            wrap=tk.WORD, relief=tk.FLAT,
            bg="#E0E0E0",
            fg=config.COLOR_BACKGROUND,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        self.text_box.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.root, bg=config.COLOR_BACKGROUND)
        button_frame.pack(pady=6)

        enabled_checker = lambda: self.buttons_enabled

        self.btn_scan = self.button_factory.create(button_frame, self.localization_manager.get_string("scan_button"), self.start_scan, enabled_checker)
        self.btn_save = self.button_factory.create(button_frame, self.localization_manager.get_string("save_button"), self.guardar_archivo, enabled_checker)
        self.btn_info = self.button_factory.create(button_frame, self.localization_manager.get_string("info_button"), self.mostrar_informacion, enabled_checker)

        self.btn_scan.grid(row=0, column=0, padx=5)
        self.btn_save.grid(row=0, column=1, padx=5)
        self.btn_info.grid(row=0, column=2, padx=5)

    def _set_buttons_state(self, enabled: bool):
        """
        Habilita o deshabilita la funcionalidad de los botones.
        """
        self.buttons_enabled = enabled
        cursor = 'hand2' if enabled else 'arrow'
        for btn in [self.btn_scan, self.btn_save, self.btn_info]:
            btn.config(cursor=cursor)

    def start_scan(self):
        """
        Inicia el proceso de escaneo.
        """
        if self.controller.is_scanning or not self.verificar_sistema():
            return

        # Llama al controlador para que inicie el escaneo. El controlador
        # actualizará su propio estado interno a 'is_scanning = True'.
        self.controller.start_scan_thread(
            on_success=self._on_scan_success,
            on_error=self._on_scan_error
        )

        # Una vez que el controlador ha iniciado, actualizamos la UI para
        # reflejar el estado de "escaneando".
        if self.controller.is_scanning:
            self.app_state.credentials = None
            self._set_buttons_state(enabled=False)
            self.spinner_anim()

    def _on_scan_success(self, credentials: List[NetworkCredential]):
        """
        Callback para cuando el escaneo es exitoso.
        """
        def update_ui():
            self.app_state.credentials = credentials
            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete("1.0", tk.END)

            if credentials:
                display_text = self.controller.format_credentials_for_display(credentials)
                self.text_box.insert(tk.END, display_text.rstrip())
                self.text_box.insert(tk.END, "\n\n" + "—" * 23) # Corrected line
                self.text_box.insert(
                    tk.END,
                    f"\n{self.localization_manager.get_string('scan_completed', len(credentials))}" # Corrected line
                )
                self.text_box.see(tk.END)
            else:
                self.text_box.insert(tk.END, self.localization_manager.get_string("no_networks_found"))

            self.text_box.config(state=tk.DISABLED)
            self._set_buttons_state(enabled=True)
        
        self.root.after(0, update_ui)

    def _on_scan_error(self, error_message: str):
        """
        Callback para cuando el escaneo falla.
        """
        def update_ui():
            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, error_message)
            self.text_box.config(state=tk.DISABLED)
            self._set_buttons_state(enabled=True)

        self.root.after(0, update_ui)
        
    def spinner_anim(self):
        """
        Controla la animación del spinner de carga.
        """
        if not self.controller.is_scanning:
            return
            
        self.app_state.spinner_index = (self.app_state.spinner_index + 1) % len(self.app_state.SPINNER)
        spinner_frame = self.app_state.SPINNER[self.app_state.spinner_index]
        
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, f"{self.localization_manager.get_string('scanning_message')} {spinner_frame}")
        self.text_box.config(state=tk.DISABLED)
        
        self.root.after(120, self.spinner_anim)

    def guardar_archivo(self):
        """
        Maneja la lógica para guardar el reporte en un archivo.
        """
        if not self.app_state.credentials:
            self.ventana_mensaje("warning_title", "first_scan_required")
            return

        default_report_name = self.localization_manager.get_string("report_default_name")
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=default_report_name,
            filetypes=[(self.localization_manager.get_string("text_files"), "*.txt")], confirmoverwrite=False
        )
        if not ruta: return

        if os.path.exists(ruta):
            if not self.ventana_confirmacion("confirm_replace_title", "confirm_replace_message"):
                return
        
        success, error_message = self.controller.save_report(ruta, self.app_state.credentials)

        if success:
            self.ventana_mensaje("success_title", "report_saved_successfully")
        else:
            self.ventana_mensaje("error_title", None, raw_message=error_message)

    def mostrar_informacion(self):
        """
        Muestra la ventana "Acerca de".
        """
        if self.app_state.info_window and self.app_state.info_window.winfo_exists():
            self.app_state.info_window.lift()
            return
        # Pasa la fábrica de botones a la ventana "Acerca de"
        self.app_state.info_window = AboutWindow(
            self.root, config, self.image_manager, self.localization_manager, self.button_factory
        )

    def centrar_ventana(self, win: tk.Toplevel | tk.Tk, w: int, h: int):
        """
        Centra una ventana dada en la pantalla.
        """
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def ventana_mensaje(self, titulo_key: str, texto_key: Optional[str], tipo: str = "info", raw_message: Optional[str] = None, *message_args):
        """
        Muestra un cuadro de diálogo de mensaje.
        """
        MessageDialog(
            parent=self.root,
            title_key=titulo_key,
            message_key=texto_key,
            config=config,
            button_factory=self.button_factory, # Pasa la fábrica
            localization_manager=self.localization_manager,
            raw_message=raw_message,
            *message_args
        )

    def ventana_confirmacion(self, titulo_key: str, texto_key: Optional[str], raw_message: Optional[str] = None, *message_args) -> bool:
        """
        Muestra un cuadro de diálogo de confirmación.
        """
        dialog = ConfirmationDialog(
            parent=self.root,
            title_key=titulo_key,
            message_key=texto_key,
            config=config,
            button_factory=self.button_factory, # Pasa la fábrica
            localization_manager=self.localization_manager,
            raw_message=raw_message,
            *message_args
        )
        return dialog.result

    def verificar_sistema(self) -> bool:
        """
        Verifica la compatibilidad del sistema.
        """
        if not self.controller.is_system_compatible():
            self.ventana_mensaje("system_incompatible_title", "system_incompatible_message", tipo="error")
            return False
        return True

class AppState:
    """
    Clase para mantener el estado de la aplicación GUI.
    """
    def __init__(self):
        self.info_window: Optional[Toplevel] = None
        self.credentials: Optional[List[NetworkCredential]] = None
        self.SPINNER = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧"]
        self.spinner_index = 0
