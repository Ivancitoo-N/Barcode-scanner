# Barcode Scanner Pro 🚀

A professional, high-performance 1D barcode scanner built with Python, OpenCV, and FastAPI. Featuring a sleek "Cyber-Glass" UI, real-time analytics, and automatic product identification.

![Preview](C:/Users/ivanc/.gemini/antigravity/brain/6cacab0d-776f-4115-8997-a664c541d017/uploaded_media_1770152238713.png)

## ✨ Features

- **Real-time 1D Barcode Detection**: Supports EAN-13, EAN-8, Code128, Code39, UPCA, UPCE.
- **Cyber-Glass UI**: Modern, glassmorphic design with neon accents and pulsating scanline effects.
- **Audio Feedback**: Synthesized "beep" sound upon successful detection.
- **Smart Scanning**: Automatically adds recognized products to the history (Auto-Add).
- **Local Memory**: Learns custom names for barcodes and suggests them for future scans.
- **Analytics Dashboard**: Real-time hourly scan activity chart using Chart.js.
- **Robust Persistence**: SQLite Database with automatic 10-minute backups.
- **Export Options**: Download your scan history as CSV or JSON.
- **Flashlight Mode**: Full-screen white illumination for better scanning in low-light environments.

## 🛠 Technology Stack

- **Backend**: FastAPI (Python), SQLAlchemy, SQLite
- **Vision**: OpenCV, pyzbar, numpy
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (Chart.js)

## 🚀 Installation & Setup

1. **Prerequisites**: Ensure you have **Python 3.8+** installed.
2. **Setup**:
   Run the startup script (Windows) to create a virtual environment and install all dependencies:
   ```cmd
   start.bat
   ```
   *Alternatively, manually:*
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## 📖 Usage

1. Open http://localhost:8000 in your browser.
2. Allow webcam access.
3. Show a barcode to the camera. 
4. **Smart Mode**: If the product is recognized via API or local memory, it's added automatically.
5. **Manual Mode**: If new, enter the product name in the popup.
6. Toggle **Flashlight Mode** (🔦/💡) if needed for extra light.

## 📁 Project Structure
- `backend/`: Core logic, vision pipeline, and database management.
- `frontend/`: Templates (HTML) and static assets (CSS, JS).
- `main.py`: Entry point for the FastAPI server.
- `barcodes.db`: Local SQLite database (auto-generated).
- `backups/`: Rotating database backups.

## 🔧 Troubleshooting

- **Camera Error**: Ensure no other application is using your webcam.
- **Slow Detection**: Improve lighting or use **Flashlight Mode**.
- **Audio Issues**: Click anywhere on the page once to enable audio playback (browser policy).

---
Developed for speed, aesthetics, and reliability. 📦💨
