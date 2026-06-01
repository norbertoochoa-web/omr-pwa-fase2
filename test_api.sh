#!/bin/bash
# ===========================================================================
# Script de prueba automatizada - OMR PWA Fase 2
# Uso: bash test_api.sh [cartilla.jpg]
# ===========================================================================

API="http://localhost:8000/api/v1"
CARTILLA="${1:-/home/rodrigo/Workspace/Imax/BACKEND/inputs/Imax/evaluacion/cartilla4.jpeg}"
PASS=0
FAIL=0

green() { echo -e "\033[32m✓ $1\033[0m"; }
red() { echo -e "\033[31m✗ $1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

bold "=========================================="
bold "  OMR PWA FASE 2 - TEST AUTOMATIZADO"
bold "=========================================="
echo "API: $API"
echo "Imagen: $CARTILLA"
echo ""

# ------------------------------------------------------------------
bold "1. HEALTH CHECK"
# ------------------------------------------------------------------
RESP=$(curl -s $API/health)
if echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='healthy'" 2>/dev/null; then
    green "Health check OK"
    ((PASS++))
else
    red "Health check falló: $RESP"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "2. LOGIN - credenciales correctas"
# ------------------------------------------------------------------
RESP=$(curl -s -X POST $API/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}')

TOKEN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
USER_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['user_id'])" 2>/dev/null)
SUBS_STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['subscription']['status'])" 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$SUBS_STATUS" = "ACTIVE" ]; then
    green "Login exitoso"
    ((PASS++))
else
    red "Login falló: $RESP"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "3. LOGIN - credenciales incorrectas"
# ------------------------------------------------------------------
RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST $API/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"wrong"}')

if [ "$RESP" = "401" ]; then
    green "Login inválido rechazado (HTTP $RESP)"
    ((PASS++))
else
    red "Login inválido no rechazado (HTTP $RESP)"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "4. VERIFICAR SUSCRIPCIÓN"
# ------------------------------------------------------------------
RESP=$(curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8000/api/v1/subscription/$USER_ID \
  -H "Authorization: Bearer $TOKEN")

if [ "$RESP" = "200" ]; then
    green "Suscripción OK (HTTP $RESP)"
    ((PASS++))
else
    red "Suscripción falló (HTTP $RESP)"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "5. CREAR SESIÓN"
# ------------------------------------------------------------------
RESP=$(curl -s -X POST $API/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test automatizado"}')

SESSION=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_token'])" 2>/dev/null)
STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

if [ -n "$SESSION" ] && [ "$STATUS" = "OPEN" ]; then
    green "Sesión creada: ${SESSION:0:8}..."
    ((PASS++))
else
    red "Sesión falló: $RESP"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "6. SUBIR + PROCESAR OMR"
# ------------------------------------------------------------------
if [ -f "$CARTILLA" ]; then
    RESP=$(curl -s -X POST $API/upload \
      -H "Authorization: Bearer $TOKEN" \
      -F "image=@$CARTILLA" \
      -F "session_id=$SESSION")

    STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
    ANSWERS=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('answers',{})))" 2>/dev/null)

    if [ "$STATUS" = "success" ]; then
        green "OMR procesado exitosamente - $ANSWERS respuestas detectadas"
        echo "$RESP" | python3 -m json.tool 2>/dev/null | head -20
        ((PASS++))
    else
        red "OMR falló: $(echo $RESP | python3 -c 'import sys,json;print(json.load(sys.stdin).get(\"error_message\",\"desconocido\"))' 2>/dev/null)"
        ((FAIL++))
    fi
else
    red "Imagen no encontrada: $CARTILLA"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "7. LISTAR SESIONES"
# ------------------------------------------------------------------
RESP=$(curl -s -o /dev/null -w "%{http_code}" $API/sessions \
  -H "Authorization: Bearer $TOKEN")

if [ "$RESP" = "200" ]; then
    green "Listado sesiones OK (HTTP $RESP)"
    ((PASS++))
else
    red "Listado sesiones falló (HTTP $RESP)"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "8. FINALIZAR SESIÓN"
# ------------------------------------------------------------------
RESP=$(curl -s -X POST $API/sessions/$SESSION/finish \
  -H "Authorization: Bearer $TOKEN")

STS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

if [ "$STS" = "COMPLETED" ]; then
    green "Sesión finalizada"
    ((PASS++))
else
    red "Finalizar sesión falló: $RESP"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "9. DESCARGAR .TXT"
# ------------------------------------------------------------------
curl -s -o /tmp/test_omr_resultados.txt \
  $API/sessions/$SESSION/download \
  -H "Authorization: Bearer $TOKEN"

if [ -s /tmp/test_omr_resultados.txt ] && head -1 /tmp/test_omr_resultados.txt | grep -q "\[SESSION\]"; then
    green ".txt Delphi 7 generado"
    echo ""
    cat /tmp/test_omr_resultados.txt
    ((PASS++))
else
    red "Descarga .txt falló"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold "10. ERROR - SIN TOKEN"
# ------------------------------------------------------------------
RESP=$(curl -s -o /dev/null -w "%{http_code}" $API/sessions)

if [ "$RESP" = "401" ]; then
    green "Sin token rechazado (HTTP $RESP)"
    ((PASS++))
else
    red "Sin token no rechazado (HTTP $RESP)"
    ((FAIL++))
fi

# ------------------------------------------------------------------
bold ""
bold "=========================================="
if [ "$FAIL" -eq 0 ]; then
    bold "  RESULTADO: $PASS/10 PRUEBAS PASARON ✅"
else
    bold "  RESULTADO: $PASS pasaron, $FAIL fallaron ❌"
fi
bold "=========================================="

exit $FAIL
