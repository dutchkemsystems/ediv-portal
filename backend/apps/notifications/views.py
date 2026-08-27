from rest_framework import permissions, viewsets

from config.permissions import IsAdminOrTGOrDeptHead

from .models import NotificationLog, NotificationTemplate
from .serializers import NotificationLogSerializer, NotificationTemplateSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["channel", "is_active"]
    search_fields = ["name", "subject"]


class NotificationLogViewSet(viewsets.ModelViewSet):
    queryset = NotificationLog.objects.select_related("template", "recipient").all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["channel", "is_sent", "recipient"]
    search_fields = ["subject", "recipient__first_name", "recipient__last_name"]
    ordering_fields = ["created_at", "sent_at"]
