RESUMEN GENERAL - IMax OMR PWA (Fase 1, 2 y 3)
================================================
Fecha: 2026-06-08
VPS: 162.35.161.249 (Interserver, Ubuntu 26.04, 2GB RAM, 38GB SSD)

================================================
ARQUITECTURA (3 repos separados)
================================================

1. omr-pwa-mobile (antes omr-pwa-fase1)
   - Frontend PWA (Progressive Web App)
   - Captura de fotos de cartillas OMR desde el celular
   - Envio al backend para procesamiento
   - Stack: HTML/CSS/JS + Vite + Service Worker
   - Repo: https://github.com/norbertoochoa-web/omr-pwa-mobile

2. omr-pwa-fase2
   - Backend API en FastAPI
   - Motor OMR (OpenCV) para deteccion de marcadores
   - PostgreSQL 16 como base de datos
   - Endpoints: auth, upload, sessions, templates, download, health
   - Repo: https://github.com/norbertoochoa-web/omr-pwa-fase2

3. omr-pwa-fase3-portal
   - Portal web para clientes
   - Login, Dashboard, QR dinamico, Demo publica
   - Descarga de resultados TXT
   - Stack: FastAPI + Jinja2 + Tailwind CDN
   - Repo: https://github.com/norbertoochoa-web/omr-pwa-fase3-portal

================================================
SERVICIOS EN VPS
================================================

 Puerto | Servicio    | URL                        | Estado
 -------|-------------|----------------------------|--------
 80     | PWA (app)   | http://162.35.161.249/     | OK 200
 8000   | API fase2   | http://162.35.161.249:8000/docs | OK 200
 8001   | Portal f3   | http://162.35.161.249:8001/portal/login | OK 200
 5432   | PostgreSQL  | (interno, solo localhost)  | OK healthy

Caddy: proxy reverso + HTTPS automatico (pendiente DNS)
Docker: 3 contenedores (postgres, api, portal)

================================================
DOMINIOS (pendiente configurar DNS)
================================================

 api.imaxing.cl    -> 162.35.161.249  (backend API)
 app.imaxing.cl    -> 162.35.161.249  (PWA frontend)
 portal.imaxing.cl -> 162.35.161.249  (portal clientes)

================================================
USUARIOS CREADOS
================================================

 Portal: admin@catolico.cl / qwerty1 (institution: catolico)

================================================
MEJORAS TECNICAS REALIZADAS
================================================

Backend (fase2):
- CLAHE preprocessing movido ANTES de erode_subtract (mejora deteccion de marcadores en bajo contraste)
- Threshold params reducidos: MIN_JUMP=15, MIN_GAP=20, CONFIDENT_SURPLUS=3
- marker_rescale_steps aumentado de 10 a 15
- Outputs organizados por institution_id/session_id

Frontend (PWA):
- Download via Web Share API (navigator.share) con fallback anchor click
- Safe-area CSS para notch iPhone
- Boton download movido antes de getUserMedia (funciona en modo fallback)
- Fallback galeria con upload directo

Portal (fase3):
- Login con JWT en cookie httponly (24h)
- QR dinamico con token de 5 min de expiracion
- Demo publica sin autenticacion
- Dashboard con sesiones, descarga TXT

Deploy:
- Host networking en portal para conectar a DB local
- Starlette 1.x: TemplateResponse requiere request como primer argumento
- Jinja2 pinneado a 3.1.4 por compatibilidad

================================================
PENDIENTE
================================================

1. Configurar DNS (api/app/portal.imaxing.cl -> 162.35.161.249)
2. Una vez DNS listo, actualizar:
   - PWA_BASE_URL en .env del portal
   - VITE_API_URL en .env del frontend y rebuild
   - Caddy automaticamente dara HTTPS
3. Probar PWA desde celular con la IP actual (http://162.35.161.249)
4. Hacer seed de client_users para otras instituciones
5. Agregar cron de limpieza para outputs antiguos
6. Mejorar deteccion de marcadores en fotos ladeadas
7. Verificar formato TXT (hoy agrupa 5, ver si deben ser 60 por linea)
