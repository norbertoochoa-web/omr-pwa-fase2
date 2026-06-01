#!/bin/bash
# =============================================================================
# setup-vps.sh  -  Configuración inicial de VPS para OMR PWA Fase 2
# Uso: bash setup-vps.sh
# =============================================================================
set -euo pipefail

echo "=========================================="
echo "  OMR PWA - Configuración de VPS"
echo "=========================================="

# 1. Instalar Docker si no está presente
if ! command -v docker &>/dev/null; then
    echo "[1/4] Instalando Docker..."
    apt-get update -qq
    apt-get install -y -qq docker.io docker-compose-v2
else
    echo "[1/4] Docker ya instalado"
fi

# 2. Crear usuario deploy si no existe (opcional)
if ! id -u deploy &>/dev/null; then
    echo "[2/4] Creando usuario 'deploy'..."
    useradd -m -s /bin/bash deploy
    usermod -aG docker deploy
    echo "  → Usuario 'deploy' creado. Usa: sudo -iu deploy"
else
    echo "[2/4] Usuario 'deploy' ya existe"
fi

# 3. Crear directorio del proyecto
PROJECT_DIR="/opt/omr-pwa"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[3/4] Creando $PROJECT_DIR..."
    mkdir -p "$PROJECT_DIR"
fi
echo "[3/4] Directorio: $PROJECT_DIR"

# 4. Recordatorio final
echo "[4/4] Listo. Próximos pasos:"
echo ""
echo "  cd $PROJECT_DIR"
echo "  git clone <tu-repo> ."
echo "  cp .env.example .env    # editar credenciales"
echo "  docker compose -f docker-compose.prod.yml up -d"
echo ""

# Verificar puertos
if ss -tlnp | grep -q ':80 '; then
    echo "⚠  Puerto 80 ya está en uso. Revisa docker-compose.prod.yml"
fi
