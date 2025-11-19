# Gesture Recognition System 🤖✋

System rozpoznawania gestów z wykorzystaniem uczenia maszynowego w przemyśle.

## 📋 Opis

Przemysłowy system do rozpoznawania gestów rąk/dłoni na żywo z kamer przemysłowych, 
z możliwością trenowania własnych gestów i kontroli maszyn.

## 🎯 Funkcjonalności

- ✅ Real-time wykrywanie gestów (MediaPipe)
- ✅ 12 gestów domyślnych (8 statycznych + 4 dynamiczne)
- ✅ Trening własnych gestów
- ✅ Wiele algorytmów ML (Random Forest, SVM, Neural Network, LSTM...)
- ✅ Multi-camera support (do 9 kamer)
- ✅ Multi-user tracking
- ✅ Emergency system (X Sign)
- ✅ Interfejs webowy (React + TypeScript)

## 🛠️ Stack Technologiczny

**Backend:**
- Python 3.10+
- FastAPI
- MediaPipe
- TensorFlow
- OpenCV
- SQLite

**Frontend:**
- React 18
- TypeScript
- Vite
- TailwindCSS

## 📂 Struktura Projektu

gesture-recognition-system/
├── backend/ # Python FastAPI backend
├── frontend/ # React TypeScript frontend
├── docker/ # Docker configuration
└── docs/ # Documentation


## 🚀 Quick Start

### Backend

cd backend
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend

cd frontend
npm install
npm run dev


## 👨‍💻 Autor

[Twoje Imię Nazwisko]  
Praca Inżynierska 2025/2026

## 📅 Timeline

- 23.11.2025 - 31.12.2025: Część praktyczna (program)
- 02.01.2026 - 31.01.2026: Część teoretyczna (praca pisemna)

## 📄 Licencja

MIT License
