# wifi_scanner/ui/i18n.py
import json
import os
import logging
from typing import Optional # Importar Optional
from config import LOCALES_DIR, DEFAULT_LANG, BASE_PATH

logger = logging.getLogger(__name__)

class I18N:
    """
    Clase para manejar la internacionalización de la aplicación.
    Carga los archivos de traducción y proporciona un método para obtener cadenas traducidas.
    """
    _instance = None

    def __new__(cls, lang: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(I18N, cls).__new__(cls)
            cls._instance._initialized = False
        if lang is not None and not cls._instance._initialized:
            cls._instance._initialize(lang)
        return cls._instance

    def _initialize(self, lang: str):
        if self._initialized:
            return
        self.current_lang = lang
        self.translations = {}
        self._load_translations()
        self._initialized = True
        logger.info(f"I18N inicializado con el idioma '{self.current_lang}'.")

    def _load_translations(self):
        """
        Carga las traducciones del archivo JSON correspondiente al idioma actual.
        Busca el archivo en la ruta BASE_PATH/LOCALES_DIR.
        """
        locale_file = os.path.join(BASE_PATH, LOCALES_DIR, f"{self.current_lang}.json")
        if not os.path.exists(locale_file):
            logger.warning(f"Archivo de traducción no encontrado para '{self.current_lang}': {locale_file}. Intentando cargar el idioma por defecto '{DEFAULT_LANG}'.")
            self.current_lang = DEFAULT_LANG
            locale_file = os.path.join(BASE_PATH, LOCALES_DIR, f"{self.current_lang}.json")
            if not os.path.exists(locale_file):
                logger.error(f"Archivo de traducción por defecto tampoco encontrado: {locale_file}.")
                self.translations = {}
                return

        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            logger.info(f"Traducciones cargadas desde: {locale_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON del archivo de traducción '{locale_file}': {e}")
            self.translations = {}
        except Exception as e:
            logger.error(f"Error inesperado al cargar traducciones desde '{locale_file}': {e}")
            self.translations = {}

    def get_text(self, key: str, *args, **kwargs) -> str:
        """
        Obtiene la cadena traducida para una clave dada.
        Permite formatear la cadena con argumentos posicionales o de palabra clave.
        """
        text = self.translations.get(key, f"KEY_NOT_FOUND: {key}")
        try:
            return text.format(*args, **kwargs)
        except IndexError:
            logger.warning(f"Faltan argumentos para formatear la clave '{key}' en el idioma '{self.current_lang}'. Texto original: '{text}'")
            return text
        except KeyError:
            logger.warning(f"Argumentos de palabra clave incorrectos para formatear la clave '{key}' en el idioma '{self.current_lang}'. Texto original: '{text}'")
            return text
        except Exception as e:
            logger.error(f"Error al formatear la clave '{key}' con texto '{text}' y args {args}, kwargs {kwargs}: {e}")
            return text
            
    def set_language(self, lang: str):
        """
        Cambia el idioma de la aplicación y recarga las traducciones.
        """
        if self.current_lang != lang:
            self.current_lang = lang
            self._load_translations()
            logger.info(f"Idioma cambiado a '{self.current_lang}'.")

# Singleton instance
i18n = I18N()
