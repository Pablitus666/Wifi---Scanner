from PIL import Image, ImageChops, ImageOps, ImageTk
import os
import tkinter as tk
from typing import Optional, Tuple, Dict

def add_shadow(image: Image.Image, offset: tuple[int, int] = (2, 2), shadow_color: tuple[int, int, int, int] = (0, 0, 0, 80)) -> Image.Image:
    """
    Añade un efecto de sombra a una imagen RGBA dada.

    Crea una silueta desplazada de la imagen original, rellena con un color de sombra
    y combinada con la imagen original para dar un efecto de profundidad.

    Args:
        image (Image.Image): La imagen PIL de entrada, se convertirá a RGBA si es necesario.
        offset (tuple[int, int]): El desplazamiento (dx, dy) de la sombra respecto a la imagen original.
                                  Defaults to (2, 2).
        shadow_color (tuple[int, int, int, int]): El color RGBA de la sombra.
                                                 Defaults to (0, 0, 0, 80) (negro semitransparente).

    Returns:
        Image.Image: Una nueva imagen PIL con el efecto de sombra aplicado.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Obtener el canal alfa de la imagen para usarlo como máscara de la sombra.
    alpha_mask = image.split()[-1]
    r, g, b, alpha_value = shadow_color

    # Crear una imagen RGB con el color de la sombra.
    shadow_img_rgb = Image.new('RGB', image.size, (r, g, b))
    
    # Escalar el canal alfa para aplicar la opacidad deseada a la sombra.
    target_alpha = Image.new('L', alpha_mask.size, color=alpha_value)
    scaled_alpha_mask = ImageChops.darker(alpha_mask, target_alpha)
    
    # Aplicar el alfa escalado a la imagen de color de la sombra.
    final_shadow_image = shadow_img_rgb.copy()
    final_shadow_image.putalpha(scaled_alpha_mask)

    # Calcular las dimensiones del lienzo extendido para acomodar la sombra y la imagen.
    # El canvas debe ser lo suficientemente grande para contener la imagen y su sombra,
    # incluyendo los offsets positivos y negativos.
    # El punto más a la izquierda o arriba es min(0, offset[0/1])
    # El punto más a la derecha o abajo es max(image.width, image.width + offset[0/1])
    min_x = min(0, offset[0])
    max_x = max(image.width, image.width + offset[0])
    min_y = min(0, offset[1])
    max_y = max(image.height, image.height + offset[1])

    canvas_width = max_x - min_x
    canvas_height = max_y - min_y
    
    # Crear un lienzo transparente donde se pegarán la sombra y la imagen.
    enhanced_image = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))

    # Calcular las posiciones para pegar la imagen original y la sombra en el nuevo lienzo.
    # El origen (0,0) del lienzo es relativo al punto más a la izquierda/arriba del contenido combinado.
    original_paste_x = -min_x
    original_paste_y = -min_y

    shadow_paste_x = original_paste_x + offset[0]
    shadow_paste_y = original_paste_y + offset[1]

    # Pegar la sombra primero y luego la imagen original encima.
    enhanced_image.paste(final_shadow_image, (shadow_paste_x, shadow_paste_y), final_shadow_image)
    enhanced_image.paste(image, (original_paste_x, original_paste_y), image)

    return enhanced_image

class ImageManager:
    """
    Gestor de imágenes para la interfaz gráfica.

    Encargado de cargar imágenes desde el disco, redimensionarlas,
    aplicar efectos como sombras y cachear las `tk.PhotoImage` resultantes
    para evitar recargas costosas y mantener las referencias necesarias para Tkinter.
    """
    def __init__(self):
        """
        Inicializa el ImageManager.

        Crea un caché interno (`_image_cache`) para almacenar las `tk.PhotoImage`
        cargadas y una lista (`_image_references`) para mantener referencias
        a las imágenes, evitando que sean recolectadas por el garbage collector
        de Python, lo que causaría que no se mostraran en Tkinter.
        """
        self._image_cache: Dict[tuple, tk.PhotoImage] = {}
        self._image_references: list[tk.PhotoImage] = []

    def load(self, path: str, size: Optional[Tuple[int, int]] = None, apply_shadow: bool = False, shadow_options: Optional[Dict] = None) -> Optional[tk.PhotoImage]:
        """
        Carga una imagen, opcionalmente la redimensiona y le aplica un efecto de sombra.

        Las imágenes procesadas se cachean para cargas futuras rápidas.

        Args:
            path (str): La ruta al archivo de imagen.
            size (Optional[Tuple[int, int]]): Una tupla (ancho, alto) para redimensionar la imagen.
                                             Si es None, la imagen no se redimensiona. Defaults to None.
            apply_shadow (bool): Si es True, aplica un efecto de sombra a la imagen.
                                 Defaults to False.
            shadow_options (Optional[Dict]): Un diccionario de opciones para la función `add_shadow`,
                                             como 'offset' y 'shadow_color'. Puede incluir 'content_offset_y'.

        Returns:
            Optional[tk.PhotoImage]: Una instancia de `tk.PhotoImage` si la imagen se carga y procesa
                                     exitosamente, o `None` si ocurre un error (ej. archivo no encontrado).
        """
        # Crear una clave de caché única para esta combinación de parámetros
        cache_key = (path, size, apply_shadow, tuple(sorted(shadow_options.items())) if shadow_options else None)

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        if not os.path.exists(path):
            print(f"ERROR: No se encuentra la imagen en la ruta: {path}")
            return None
        
        try:
            image = Image.open(path).convert("RGBA")
            
            content_offset_y = 0
            if apply_shadow:
                shadow_opts = shadow_options.copy() if shadow_options else {} # Create a copy
                content_offset_y = shadow_opts.pop('content_offset_y', 0) # Extract content_offset_y
                image = add_shadow(image, **shadow_opts) # Pass remaining shadow options to add_shadow

            # Apply content_offset_y if specified, *after* shadow has been applied
            if content_offset_y != 0:
                new_canvas_width = image.width
                new_canvas_height = image.height + content_offset_y # Extend canvas downwards
                
                shifted_image = Image.new('RGBA', (new_canvas_width, new_canvas_height), (0, 0, 0, 0))
                shifted_image.paste(image, (0, content_offset_y), image) # Paste image shifted down
                image = shifted_image # Use the shifted image

            # Redimensionar la imagen a las dimensiones finales solicitadas.
            if size:
                image = image.resize(size, Image.Resampling.LANCZOS)

            # Convertir la imagen PIL a un formato que Tkinter pueda usar.
            photo_image = ImageTk.PhotoImage(image)
            
            # Guardar en caché y mantener una referencia para evitar que sea
            # recolectada por el garbage collector de Python.
            self._image_cache[cache_key] = photo_image
            self._image_references.append(photo_image)
            
            return photo_image

        except Exception as e:
            print(f"ERROR: No se pudo cargar o procesar la imagen {path}: {e}")
            return None