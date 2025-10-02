
# Sala 1 — Backend Django + DRF (GHL Appointments)

Implementa 3 endpoints contra la API de Calendarios de GoHighLevel (LeadConnector):

- **POST** `/api/appointments/create/` — Crear cita
- **GET** `/api/appointments/list/?calendarId=...` — Listar citas por calendario
- **DELETE** `/api/appointments/cancel/<appointmentId>/` — Cancelar cita

La app guarda localmente los `appointmentId` en SQLite.

## Requisitos
- Python 3.11+
- Pip

## Instalación
```bash
pip install -r requirements.txt
python manage.py migrate
cp .env.example .env
# edita .env con tu token
```

## Variables de entorno (.env)
Ver `.env.example`. Valores por defecto orientados a **Sala 1**:

- `GHL_LOCATION_ID=CRlTCqv7ASS9xOpPQ59O`
- `GHL_ACCESS_TOKEN=...` (token basado en Location)
- `GHL_API_VERSION=2021-04-15`

## Ejecutar
```bash
python manage.py runserver 0.0.0.0:8000
```

## Pruebas rápidas (curl)
### Crear
```bash
curl -X POST http://localhost:8000/api/appointments/create/   -H "Content-Type: application/json"   -d '{
    "calendarId": "TU_CALENDAR_ID",
    "contactId": "TU_CONTACT_ID",
    "startTime": "2025-09-29T16:00:00-05:00",
    "endTime": "2025-09-29T16:30:00-05:00",
    "title": "Consulta"
  }'
```

### Listar
```bash
curl "http://localhost:8000/api/appointments/list/?calendarId=TU_CALENDAR_ID"
```

### Cancelar
```bash
curl -X DELETE "http://localhost:8000/api/appointments/cancel/APPOINTMENT_ID"
```

## Notas
- Asegúrate de que tu token tenga permisos en la **subcuenta** correcta.
- Si recibes 4xx/5xx, el backend responde con el body bruto de GHL para facilitar debugging.
