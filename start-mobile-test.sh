#!/bin/bash
# start-mobile-test.sh - Inicia entorno de prueba móvil
# Uso: bash start-mobile-test.sh

set -e

BACKEND_PORT=8000
FRONTEND_DIR="/home/rodrigo/Workspace/Imax/Mobil_web/omr-pwa-fase1/frontend"
BACKEND_URL="http://localhost:$BACKEND_PORT/api/v1"

cleanup() {
    echo ""
    echo "Limpiando procesos..."
    jobs -p | xargs -r kill 2>/dev/null
    wait 2>/dev/null
    echo "Detenido."
}
trap cleanup EXIT INT TERM

echo "=== Verificando backend ==="
if ! curl -sf "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✗ Backend no responde en $BACKEND_URL"
    echo "  Ejecuta primero: docker compose up -d"
    exit 1
fi
echo "✓ Backend OK ($BACKEND_URL)"

echo ""
echo "=== Selecciona modo de conexión ==="
IP=$(ip route get 1 | awk '{print $7;exit}')
echo "  1) Red local (WiFi) → http://$IP:$BACKEND_PORT"
echo "  2) ngrok (acceso externo)"
read -rp "  Opción [1]: " MODO
MODO=${MODO:-1}

if [ "$MODO" = "2" ]; then
    echo ""
    echo "Iniciando ngrok tunnel a puerto $BACKEND_PORT..."
    ngrok http "$BACKEND_PORT" --log=stdout > /dev/null &
    NGROK_PID=$!
    sleep 4
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c \
        "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "")
    if [ -z "$NGROK_URL" ]; then
        echo "✗ Error al obtener URL de ngrok"
        exit 1
    fi
    VITE_API_URL="$NGROK_URL/api/v1"
    echo "✓ ngrok URL: $NGROK_URL"
else
    VITE_API_URL="http://$IP:$BACKEND_PORT/api/v1"
fi

echo ""
echo "=== Iniciando frontend ==="
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Instalando dependencias..."
    cd "$FRONTEND_DIR" && npm install
fi

cd "$FRONTEND_DIR"
VITE_API_URL="$VITE_API_URL" npx vite --host 0.0.0.0 --port 5173 &
VITE_PID=$!
sleep 3

echo ""
echo "========================================"
echo "  Todo listo!"
echo ""
echo "  Abre en tu celular (misma red WiFi):"
echo "  → http://$IP:5173"
echo ""
if command -v python3 &> /dev/null; then
    python3 -c "
try:
    import qrcode
    qr = qrcode.QRCode()
    qr.add_data('http://$IP:5173')
    qr.print_ascii()
except:
    pass
" 2>/dev/null || true
fi
echo ""
echo "  Usuario: admin@test.com"
echo "  Password: password123"
echo ""
echo "  Presiona Enter para detener todo..."
echo "========================================"

read -r
