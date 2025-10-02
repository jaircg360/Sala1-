from django.urls import path
from .views import (
    CreateAppointmentView,
    ListAppointmentsView,
    CancelAppointmentView,
    UpdateAppointmentView,
)

urlpatterns = [
    path("create/", CreateAppointmentView.as_view(), name="create-appointment"),
    path("list/", ListAppointmentsView.as_view(), name="list-appointments"),
    path("cancel/<str:appointmentId>/", CancelAppointmentView.as_view(), name="cancel-appointment"),
    path("update/<str:appointmentId>/", UpdateAppointmentView.as_view(), name="update-appointment"),
]
