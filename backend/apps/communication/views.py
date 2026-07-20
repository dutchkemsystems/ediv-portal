from rest_framework import viewsets, permissions, filters
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Message, UserNotification, Circular
from .serializers import (
    MessageSerializer, MessageListSerializer,
    UserNotificationSerializer, CircularSerializer
)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('sender').prefetch_related('recipients').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['message_type', 'priority', 'is_read']
    search_fields = ['subject', 'body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['created_at', 'priority']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MessageListSerializer
        return MessageSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(recipients=user)
        ).distinct()


class UserNotificationViewSet(viewsets.ModelViewSet):
    queryset = UserNotification.objects.select_related('user').all()
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user)


class CircularViewSet(viewsets.ModelViewSet):
    queryset = Circular.objects.select_related('issued_by').all()
    serializer_class = CircularSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['priority', 'is_active']
    search_fields = ['title', 'reference_number']
    ordering_fields = ['effective_date', 'created_at']
