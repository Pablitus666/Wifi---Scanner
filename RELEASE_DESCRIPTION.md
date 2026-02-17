# 📦 WiFi Scanner v1.0.1 — Modular Architecture & Stability Patch

🎉 **First Stable Modular Release with Stability Patches**

Versión de mantenimiento para el WiFi Scanner de Windows. Esta versión refina la arquitectura modular, corrige errores y mejora la estabilidad general de la aplicación tras la gran refactorización.

La aplicación permite escanear redes Wi‑Fi almacenadas en el sistema, visualizar credenciales (cuando el sistema lo permite) y generar reportes profesionales en formato `.txt`.

---

## 🔧 Cambios en esta versión (v1.0.1)

Esta versión de mantenimiento se centra en la estabilidad y la corrección de errores surgidos tras la refactorización modular:

* **Corrección de Spinner:** Se solucionó una regresión que impedía que la animación de "escaneando" se mostrara correctamente.
* **Refactorización de Estado:** Se centralizó el estado `is_scanning` en el `Controller` para eliminar redundancias y posibles condiciones de carrera, haciendo la comunicación entre la UI y el backend más robusta.
* **Corrección de Sintaxis:** Se solucionó un `SyntaxError` inicial que ocurría por un manejo incorrecto de strings multilínea.

---

## ✨ Características Principales

* 🔍 **Escaneo de Perfiles:** Detecta todos los perfiles Wi‑Fi almacenados en Windows.
* 🔐 **Recuperación de Contraseñas:** Muestra las contraseñas de redes guardadas (requiere ejecución como administrador).
* ⚡ **UI Reactiva:** El escaneo se ejecuta en un hilo separado para mantener la interfaz de usuario siempre fluida y sin bloqueos.
* ⏳ **Feedback Visual:** Un spinner animado informa al usuario que el escaneo está en progreso.
* 🌍 **Soporte Multilenguaje:** Detecta automáticamente el idioma del sistema y traduce la interfaz.
* 📄 **Reportes Profesionales:** Genera reportes detallados en formato `.txt`.
* 🪵 **Logging Detallado:** Crea un log rotativo para facilitar la depuración.
* 🛡️ **Validaciones Automáticas:** Verifica la compatibilidad del sistema operativo y los permisos necesarios.
* 🧱 **Arquitectura Modular:** Código desacoplado en capas (`core`, `infrastructure`, `ui`, etc.) para máxima mantenibilidad.

---

## 🏗️ Arquitectura

Estructura desacoplada en capas:

* `application/` → Orquestación (Controller)
* `core/` → Lógica de negocio
* `infrastructure/` → Acceso a sistema (netsh)
* `ui/` → Interfaz gráfica Tkinter
* `utils/` → Utilidades y localización
* `assets/` → Recursos como imágenes e íconos
* `logs/` → Logging rotativo

Principios aplicados:

* Separación de responsabilidades
* Inyección de dependencias
* Arquitectura orientada a servicios
* Logging centralizado
* Internacionalización (i18n)

---

## 🖥️ Requisitos del Sistema

* Windows 10 / 11
* Permisos de administrador (para obtener contraseñas)
* Python NO requerido (incluido en el ejecutable)

---

## 📄 Reporte Generado

El archivo `.txt` incluye:

* Banner ASCII
* Fecha y hora del escaneo
* Usuario del sistema
* Sistema operativo
* Lista de redes Wi‑Fi y contraseñas disponibles
* Firma del desarrollador

ℹ️ La cantidad de redes encontradas se muestra en pantalla pero no se guarda en el archivo.

---

## 📦 Empaquetado y Firma

* **Herramienta:** PyInstaller
* **Modo:** `--onefile`
* **Tipo:** Aplicación de escritorio (sin consola).
* **Elevación de Privilegios:** Se incluye un manifiesto (`admin.manifest`) que solicita permisos de administrador al ejecutar, necesarios para la recuperación de contraseñas.
* **Firma Digital:** Se proporciona el script `firmar_app.ps1` para generar un certificado de desarrollo autofirmado y firmar el `.exe`. Esto mejora la confianza a nivel local pero no es un certificado emitido por una Autoridad de Certificación (CA).

La distribución final es un único archivo **portable** (`.exe`) que no requiere instalación.

---

## ⚠️ Aviso Legal

Este software accede a contraseñas Wi‑Fi almacenadas localmente en el sistema.

Debe utilizarse únicamente en equipos propios o con autorización expresa del propietario.

El desarrollador no se responsabiliza por el uso indebido de la herramienta.

---

## 👨‍💻 Autor

**Pablo Téllez**  
Desarrollador de Software  

📍 Tarija, Bolivia <img src="https://flagcdn.com/w20/bo.png" width="20"/> <br>
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — WiFi Scanner

---

📥 Descarga el ejecutable desde la sección **Assets** de este release.
