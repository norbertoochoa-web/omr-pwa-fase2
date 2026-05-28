#!/bin/bash
echo "=== Iniciando OMR PWA Fase 2 ==="

if ! command -v docker &> /dev/null; then
    echo "Docker no encontrado. Usando modo local..."
    echo "Asegúrate de tener PostgreSQL y Redis corriendo."
    echo ""
    echo "Instalando dependencias..."
    pip install -r requirements.txt

    echo "Sembrando base de datos..."
    python -m app.seed

    echo "Iniciando API..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Usando Docker Compose..."
    docker compose up --build -d

    echo ""
    echo "=== API disponible en http://localhost:8000 ==="
    echo "=== Documentación: http://localhost:8000/docs ==="
fi
