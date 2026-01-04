# Gesture Recognition System

System rozpoznawania gestów z wykorzystaniem uczenia maszynowego w przemyśle.

## Opis

Przemysłowy system do rozpoznawania gestów rąk/dłoni na żywo z kamer przemysłowych, 
z możliwością trenowania własnych gestów i kontroli maszyn.

## Funkcjonalności

- Real-time wykrywanie gestów (MediaPipe)
- 12 gestów domyślnych (8 statycznych)
- Trening własnych gestów
- Multi-camera support (do 9 kamer)
- Multi-user tracking
- Interfejs webowy (React + TypeScript)

## Stack Technologiczny

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

## Struktura Projektu

gesture-recognition-system/
├── backend/ # Python FastAPI backend
├── frontend/ # React TypeScript frontend
├── docker/ # Docker configuration
└── docs/ # Documentation


## Quick Start

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

## 📄 Licencja

MIT License
