import logging
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    CreateAppointmentSerializer,
    ListAppointmentsQuerySerializer,
    CancelAppointmentSerializer,
)
from .models import Appointment

logger = logging.getLogger(__name__)


def ghl_headers():
    token = settings.GHL_ACCESS_TOKEN
    if not token:
        raise RuntimeError("GHL_ACCESS_TOKEN no está configurado en el entorno (.env)")
    return {
        "Authorization": f"Bearer {token}",
        "Version": settings.GHL_API_VERSION,
        "Content-Type": "application/json",
        "Location-Id": settings.GHL_LOCATION_ID,
    }


class CreateAppointmentView(APIView):
    def post(self, request):
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payload = {
            "calendarId": data["calendarId"],
            "locationId": settings.GHL_LOCATION_ID,
            "contactId": data["contactId"],
            "startTime": data["startTime"].isoformat(),
            "endTime": data["endTime"].isoformat(),
        }
        for opt in ["title", "appointmentStatus", "assignedUserId", "toNotify", "ignoreFreeSlotValidation"]:
            if opt in data:
                payload[opt] = data[opt]

        url = f"{settings.GHL_BASE_URL}/calendars/events/appointments"
        try:
            resp = requests.post(url, headers=ghl_headers(), json=payload, timeout=20)
            resp.raise_for_status()
            body = resp.json()
        except requests.HTTPError as e:
            logger.exception("Error HTTP de GHL al crear cita")
            return Response({"detail": str(e), "body": getattr(e.response, "text", "")},
                            status=e.response.status_code if e.response else 502)
        except requests.RequestException as e:
            logger.exception("Fallo de red al crear cita")
            return Response({"detail": "Error de red contra GHL", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        ghl_id = body.get("id") or body.get("appointment", {}).get("id")
        if ghl_id:
            Appointment.objects.update_or_create(
                ghl_id=ghl_id,
                defaults={
                    "calendar_id": data["calendarId"],
                    "contact_id": data["contactId"],
                    "start_time": data["startTime"],
                    "end_time": data["endTime"],
                    "status": payload.get("appointmentStatus", "confirmed"),
                    "raw": body,
                }
            )

        return Response(body, status=status.HTTP_201_CREATED)


class ListAppointmentsView(APIView):
    def get(self, request):
        q = ListAppointmentsQuerySerializer(data=request.query_params)
        q.is_valid(raise_exception=True)
        params = {
            "calendarId": q.validated_data["calendarId"],
            "locationId": settings.GHL_LOCATION_ID,
        }
        if "contactId" in q.validated_data:
            params["contactId"] = q.validated_data["contactId"]
        if "dateFrom" in q.validated_data:
            params["dateFrom"] = q.validated_data["dateFrom"].isoformat()
        if "dateTo" in q.validated_data:
            params["dateTo"] = q.validated_data["dateTo"].isoformat()

        url = f"{settings.GHL_BASE_URL}/calendars/events/appointments"
        try:
            resp = requests.get(url, headers=ghl_headers(), params=params, timeout=20)
            resp.raise_for_status()
            body = resp.json()
        except requests.HTTPError as e:
            logger.exception("Error HTTP de GHL al listar citas")
            return Response({"detail": str(e), "body": getattr(e.response, "text", "")},
                            status=e.response.status_code if e.response else 502)
        except requests.RequestException as e:
            logger.exception("Fallo de red al listar citas")
            return Response({"detail": "Error de red contra GHL", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        return Response(body, status=status.HTTP_200_OK)


class CancelAppointmentView(APIView):
    """
    ❌ DELETE → eliminar completamente la cita
    """
    def delete(self, request, appointmentId: str):
        _ = CancelAppointmentSerializer(data={"appointmentId": appointmentId})
        _.is_valid(raise_exception=True)

        url = f"{settings.GHL_BASE_URL}/calendars/events/{appointmentId}"

        try:
            resp = requests.delete(url, headers=ghl_headers(), timeout=20)
            resp.raise_for_status()
            body = resp.json() if resp.content else {"status": "deleted"}
        except requests.HTTPError as e:
            logger.exception("Error HTTP de GHL al cancelar evento/cita")
            return Response({"detail": str(e), "body": getattr(e.response, "text", "")},
                            status=e.response.status_code if e.response else 502)
        except requests.RequestException as e:
            logger.exception("Fallo de red al cancelar evento/cita")
            return Response({"detail": "Error de red contra GHL", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        try:
            ap = Appointment.objects.get(ghl_id=appointmentId)
            ap.status = "canceled"
            ap.save(update_fields=["status", "updated_at"])
        except Appointment.DoesNotExist:
            pass

        return Response(body, status=status.HTTP_200_OK)


class UpdateAppointmentView(APIView):
    """
    ✏️ PUT → actualizar cita (ej. appointmentStatus = cancelled)
    """
    def put(self, request, appointmentId: str):
        payload = request.data

        if "appointmentStatus" not in payload:
            return Response({"error": "appointmentStatus es requerido"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = f"{settings.GHL_BASE_URL}/calendars/events/appointments/{appointmentId}"

        try:
            resp = requests.put(url, headers=ghl_headers(), json=payload, timeout=20)
            resp.raise_for_status()
            body = resp.json()
        except requests.HTTPError as e:
            logger.exception("Error HTTP de GHL al actualizar cita")
            return Response({"detail": str(e), "body": getattr(e.response, "text", "")},
                            status=e.response.status_code if e.response else 502)
        except requests.RequestException as e:
            logger.exception("Fallo de red al actualizar cita")
            return Response({"detail": "Error de red contra GHL", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        try:
            ap = Appointment.objects.get(ghl_id=appointmentId)
            ap.status = payload["appointmentStatus"]
            ap.save(update_fields=["status", "updated_at"])
        except Appointment.DoesNotExist:
            pass

        return Response(body, status=status.HTTP_200_OK)
