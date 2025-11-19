# Backend - Gesture Recognition System

FastAPI backend z ML pipeline.

## Setup

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## Run

uvicorn app.main:app --reload

API docs: http://localhost:8000/docs

## Structure

app/
├── api/ # API routes
├── core/ # Config, database
├── models/ # SQLAlchemy models
├── services/ # Business logic
└── utils/ # Utilities

undefined