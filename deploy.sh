#!/bin/bash
# =============================================================================
# deploy.sh  -  Despliegue / actualización en VPS
#
# Uso en VPS:
#   bash deploy.sh                # construir y levantar
#   bash deploy.sh --restart      # solo reiniciar servicios
#   bash deploy.sh --logs         # ver logs
#   bash deploy.sh --down         # detener todo
# =============================================================================
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
ACTION="${1:-up}"

case "$ACTION" in
    up|--up)
        echo "🚀 Construyendo y levantando servicios..."
        docker compose -f "$COMPOSE_FILE" build --pull
        docker compose -f "$COMPOSE_FILE" up -d
        echo ""
        echo "✅ API: http://localhost/api/v1/health"
        echo "📄 Logs: docker compose -f $COMPOSE_FILE logs -f"
        ;;
    restart|--restart)
        echo "🔄 Reiniciando servicios..."
        docker compose -f "$COMPOSE_FILE" restart
        ;;
    logs|--logs)
        echo "📄 Logs en tiempo real..."
        docker compose -f "$COMPOSE_FILE" logs -f
        ;;
    down|--down)
        echo "⏹  Deteniendo servicios..."
        docker compose -f "$COMPOSE_FILE" down
        ;;
    status|--status)
        echo "📊 Estado de servicios:"
        docker compose -f "$COMPOSE_FILE" ps
        ;;
    *)
        echo "Uso: bash deploy.sh [up|restart|logs|down|status]"
        exit 1
        ;;
esac
