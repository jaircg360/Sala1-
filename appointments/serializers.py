from rest_framework import serializers

class CreateAppointmentSerializer(serializers.Serializer):
    calendarId = serializers.CharField()
    contactId = serializers.CharField()
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    title = serializers.CharField(required=False, allow_blank=True)
    appointmentStatus = serializers.CharField(required=False, allow_blank=True)
    assignedUserId = serializers.CharField(required=False, allow_blank=True)
    toNotify = serializers.BooleanField(required=False, default=False)
    ignoreFreeSlotValidation = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        if data["endTime"] <= data["startTime"]:
            raise serializers.ValidationError("endTime debe ser mayor que startTime")
        return data

class ListAppointmentsQuerySerializer(serializers.Serializer):
    calendarId = serializers.CharField()
    contactId = serializers.CharField(required=False)
    dateFrom = serializers.DateField(required=False)
    dateTo = serializers.DateField(required=False)

class CancelAppointmentSerializer(serializers.Serializer):
    appointmentId = serializers.CharField()
