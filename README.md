# Barcode Scanner Pro 🚀

Un escáner de códigos de barras 1D de alto rendimiento y grado profesional, construido con Python, OpenCV y FastAPI. Cuenta con una elegante interfaz "Cyber-Glass", analíticas en tiempo real e identificación automática de productos.

![Vista Previa](https://raw.githubusercontent.com/Ivancitoo-N/Barcode-scanner/main/brain/uploaded_media_1770152238713.png)

## ✨ Características

- **Detección de Códigos 1D en Tiempo Real**: Soporta EAN-13, EAN-8, Code128, Code39, UPCA, UPCE.
- **Interfaz Cyber-Glass**: Diseño moderno y glassmórfico con acentos neón y efectos de escaneo pulsantes.
- **Feedback Auditivo**: Sonido "beep" sintetizado tras cada detección exitosa.
- **Escaneo Inteligente**: Añade automáticamente productos reconocidos al historial (Auto-Add).
- **Memoria Local**: Aprende nombres personalizados para códigos de barras y los sugiere en futuros escaneos.
- **Panel de Analíticas**: Gráfico interactivo de actividad de escaneo por horas (Chart.js).
- **Persistencia Robusta**: Base de datos SQLite con copias de seguridad automáticas cada 10 minutos.
- **Exportación a PDF Profesional**: Genera facturas detalladas con agrupación de productos, cantidades y totales calculados.
- **Seguimiento de Ventas (Excel)**: Registro automático de transacciones en `sales.xlsx` para futuro control de stock.
- **Flujo de Trabajo para Clientes**: Sistema de "Nuevo Cliente" que permite cerrar ventas y exportar datos de forma organizada.
- **Base de Datos de Precios**: Ahora registra el precio unitario y total de cada escaneo.
- **Opciones de Exportación**: Descarga tu historial en formatos CSV, JSON o PDF.
- **Modo Linterna**: Iluminación blanca a pantalla completa para escanear en entornos con poca luz.

## 🛠 Tecnologías Utilizadas

- **Backend**: FastAPI (Python), SQLAlchemy, SQLite
- **Visión Artificial**: OpenCV, pyzbar, numpy
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Chart.js)

## 🚀 Super Instalación (Un solo comando)

Copia y pega esto en tu terminal (CMD o PowerShell) para clonar y arrancar el proyecto al instante:

```bash
git clone https://github.com/Ivancitoo-N/Barcode-scanner.git && cd Barcode-scanner && start.bat
```

---

## 🛠 Instalación Paso a Paso (Manual)

1. **Requisitos**: Asegúrate de tener **Python 3.8+** instalado.
2. **Configuración**:
   Ejecuta el script de inicio (Windows) para crear el entorno virtual e instalar las dependencias automáticamente:
   ```cmd
   start.bat
   ```
   *Alternativamente, de forma manual:*
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## 📖 Modo de Uso

1. Abre http://localhost:8000 en tu navegador.
2. Permite el acceso a la cámara.
3. Muestra un código de barras a la cámara. 
4. **Modo Inteligente**: Si el producto se reconoce por API o memoria local, se añade solo.
5. **Modo Manual**: Si es nuevo, introduce el nombre en la ventana emergente.
6. Activa el **Modo Linterna** (🔦/💡) si necesitas luz extra.

## 📁 Estructura del Proyecto
- `backend/`: Lógica central, procesamiento de visión y gestión de base de datos.
- `frontend/`: Plantillas (HTML) y archivos estáticos (CSS, JS).
- `main.py`: Punto de entrada del servidor FastAPI.
- `barcodes.db`: Base de datos SQLite (generada automáticamente).
- `backups/`: Copias de seguridad rotativas.

## 🔧 Solución de Problemas

- **Error de Cámara**: Asegúrate de que ninguna otra aplicación esté usando la cámara.
- **Detección Lenta**: Mejora la iluminación o usa el **Modo Linterna**.
- **Problemas de Audio**: Haz clic en cualquier parte de la página una vez para habilitar el sonido (política del navegador).

---
Desarrollado para ofrecer velocidad, estética y fiabilidad. 📦💨
