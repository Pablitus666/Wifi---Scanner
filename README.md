# 📡 WiFi Scanner (Windows) — Modular Architecture Edition

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![GUI](https://img.shields.io/badge/GUI-Tkinter-success)
![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-informational)
![Build](https://img.shields.io/badge/Build-PyInstaller-orange)
![Installer](https://img.shields.io/badge/Installer-Inno%20Setup-critical)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Aplicación de escritorio desarrollada en **Python** que permite escanear redes Wi‑Fi almacenadas en Windows, visualizar sus credenciales (cuando el sistema lo permite) y generar reportes profesionales en formato `.txt`.

Esta versión corresponde a la **edición modular refactorizada**, basada en principios de separación de responsabilidades y arquitectura limpia.

---

![WiFi Scanner Preview](https://raw.githubusercontent.com/Pablitus666/Pablitus666-Wifi---Scanner/main/images2/Preview.png)

---

## 🏗️ Arquitectura del Proyecto

El proyecto fue migrado desde una versión monolítica a una estructura desacoplada por capas, facilitando su mantenimiento y escalabilidad:

```
wifi_scanner/
│
├── application/        # Orquestación (Controller)
├── core/               # Lógica de negocio e interfaces
├── infrastructure/     # Acceso a sistema (netsh, validaciones)
├── ui/                 # Interfaz gráfica (Tkinter)
├── utils/              # Utilidades (localización, recursos)
│
├── assets/             # Imágenes, íconos y archivos de localización
├── logs/               # Archivos de log rotativos
├── tests/              # Pruebas (si aplican)
│
├── main.py             # Punto de entrada de la aplicación
├── config.py           # Configuración central
├── Wifi_Scanner.spec   # Especificación de PyInstaller
├── firmar_app.ps1      # Script de firmado (certificado autofirmado)
└── admin.manifest      # Manifiesto de elevación de privilegios
```

### Principios aplicados

* **Separación de Responsabilidades (SoC):** Cada módulo tiene un propósito claro y definido.
* **Inyección de Dependencias (DI):** Las dependencias se inyectan desde el exterior, facilitando las pruebas y el desacoplamiento.
* **Arquitectura Orientada a Servicios:** La lógica de negocio se expone a través de servicios.
* **Logging Centralizado:** Uso de `RotatingFileHandler` para un registro de eventos robusto.
* **Internacionalización (i18n):** Soporte para múltiples idiomas mediante archivos JSON.
* **Empaquetado Robusto:** Configuración avanzada para PyInstaller que asegura la inclusión de todos los recursos.

---

## ✨ Características

* 🔍 **Escaneo de Perfiles:** Detecta todos los perfiles Wi‑Fi almacenados en Windows.
* 🔐 **Recuperación de Contraseñas:** Muestra las contraseñas de redes guardadas (requiere ejecución como administrador).
* ⚡ **UI Reactiva:** El escaneo se ejecuta en un hilo separado para mantener la interfaz de usuario siempre fluida y sin bloqueos.
* ⏳ **Feedback Visual:** Un spinner animado informa al usuario que el escaneo está en progreso.
* 🌍 **Soporte Multilenguaje:** Detecta automáticamente el idioma del sistema y traduce la interfaz.
* 📄 **Reportes Profesionales:** Genera reportes detallados en formato `.txt`.
* 🪵 **Logging Detallado:** Crea un log rotativo en la carpeta `/logs` para facilitar la depuración.
* 🛡️ **Validaciones Automáticas:** Verifica la compatibilidad del sistema operativo y los permisos necesarios.
* 📦 **Ejecutable Portable:** Se distribuye como un único archivo `.exe` que no requiere instalación.

---

## 🖥️ Requisitos del Sistema

* Windows 10 / 11
* Permisos de administrador (para obtener contraseñas)
* Python 3.10+ (solo si se ejecuta desde código fuente)

---

## 📦 Dependencias

La aplicación utiliza únicamente una dependencia externa:

```
Pillow>=10.0.0
```

El resto de módulos pertenecen a la librería estándar de Python.

Instalación:

```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución

### ▶ Desde código fuente

```bash
python main.py
```

---

### 📦 Ejecutable (.exe)

1. Descargar el archivo .exe desde la sección **Releases** del repositorio.
2. Ejecutar directamente el archivo (no requiere instalación).
3. El ejecutable es portable, no genera instalador ni modifica el sistema.


---

## 📷 Capturas de pantalla

<p align="center">
  <img src="images2/screenshot.png?v=2" alt="Vista previa de la aplicación" width="600"/>
</p>

---

## 🛠️ Flujo Interno de la Aplicación

1. `main.py`

   * Configura logging
   * Inicializa localización
   * Inyecta dependencias en Controller
   * Lanza la GUI

2. `Controller`

   * Valida sistema
   * Verifica privilegios
   * Ejecuta escaneo en hilo separado
   * Orquesta generación de reportes

3. `WiFiScannerService`

   * Solicita perfiles Wi‑Fi
   * Obtiene credenciales mediante proveedor netsh

4. `ReportService`

   * Genera contenido formateado
   * Guarda archivo en disco

---

## 🪵 Logging

Se utiliza `RotatingFileHandler`:

* Tamaño máximo configurable
* Copias de respaldo automáticas
* Logs en carpeta `/logs`

Formato:

```
fecha - módulo - nivel - mensaje
```

---

## 🌍 Internacionalización

El sistema detecta automáticamente el idioma del sistema operativo y carga el archivo JSON correspondiente desde `/assets/locales`.

Si no existe traducción disponible, se utiliza inglés por defecto.

---

## 📦 Empaquetado

El ejecutable fue generado con:

* PyInstaller (configuración avanzada mediante `.spec`)
* Elevación mediante `admin.manifest`
* Script de firmado (`firmar_app.ps1`)

---

## ⚠️ Aviso Legal

Esta aplicación muestra contraseñas Wi‑Fi almacenadas localmente en el sistema.

Debe utilizarse únicamente en equipos propios o con autorización expresa del propietario.

El desarrollador no se responsabiliza por el uso indebido de la herramienta.

---

## 🧭 Versión Anterior (Legacy)

⚠️ Este proyecto reemplaza la versión monolítica original.

La versión anterior se conserva únicamente con fines históricos y educativos.
No recibe nuevas funcionalidades ni mantenimiento.

---

## 👨‍💻 Autor

**Walter Pablo Téllez Ayala**  
Software Developer

📍 Tarija, Bolivia <img src="https://flagcdn.com/w20/bo.png" width="20"/> <br>
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — WiFi Scanner

---

⭐ Si el proyecto te resulta útil, considera dejar una estrella en el repositorio.
