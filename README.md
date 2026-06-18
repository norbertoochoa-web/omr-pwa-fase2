# OMR PWA — Backend API

API FastAPI para procesamiento OMR de cartillas de respuestas.

## Changelog

| Fecha | Modelo IA | Archivo(s) | Cambio |
|---|---|---|---|
| 2026-06-17 | deepseek-v4-flash-free | `app/omr_engine/core.py` | Fix: bajar threshold floor 95→85 para detectar marcas suaves; evitar falsos negativos multi-marca |
| 2026-06-17 | deepseek-v4-flash-free | `app/omr_engine/defaults.py` | Fix: ajustar AutoAlign max_steps 20→30 para mayor precisión en alineación |
| 2026-06-17 | deepseek-v4-flash-free | `app/routes/auth.py` | Fix: aceptar type `pwa_sso` y `qr_access` en SSO; agregar logger.warning para debug |
| 2026-06-17 | deepseek-v4-flash-free | `app/routes/auth.py` | Fix: buscar usuario via `client_users` JOIN por email en vez de sessions |
| 2026-06-17 | deepseek-v4-flash-free | `app/routes/auth.py`, `app/schemas/auth.py` | Feat: endpoint `POST /auth/sso` para exchange de token QR |
| 2026-06-14 | deepseek-v4-flash-free | `app/omr_engine/core.py` | Cleanup: quitar logs debug, simplificar safety cap |
| 2026-06-13 | deepseek-v4-flash-free | `app/omr_engine/core.py`, `app/omr_engine/image_utils.py` | Fix: safety cap por marked_ratio (>85% → p85+15); fix normalize_util dst=None |
| 2026-06-12 | deepseek-v4-flash-free | `app/omr_engine/core.py` | Feat: umbral global mixto gap+otsu (60/40) con clamp [95,210] |
| 2026-06-11 | deepseek-v4-flash-free | `app/omr_engine/core.py` | Fix: bajar floor global_thr 165→100 y MIN_JUMP 25→15 |
| 2026-06-10 | deepseek-v4-flash-free | `app/omr_engine/evaluation.py`, `app/services/omr_service.py`, `app/services/txt_service.py` | Feat: multi-marked → "ERROR" en DB y "E" en TXT |
| 2026-06-09 | deepseek-v4-flash-free | `app/main.py`, `app/config.py` | Feat: DATA_DIR persistente en `/var/omr/data`, StaticFiles montado en `/data` |
| 2026-06-09 | deepseek-v4-flash-free | `docker-compose.prod.yml` | Fix: port 8000:8000 (evitar conflicto con Caddy) |
