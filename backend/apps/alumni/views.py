from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AlumniMember, AlumniEvent, AlumniDonation
from .serializers import (
    AlumniMemberSerializer, AlumniEventSerializer, AlumniDonationSerializer
)


class AlumniMemberViewSet(viewsets.ModelViewSet):
    queryset = AlumniMember.objects.select_related('user', 'school').all()
    serializer_class = AlumniMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'graduation_year', 'is_active_alumni', 'is_donor']
    search_fields = ['user__first_name', 'user__last_name', 'current_occupation']
    ordering_fields = ['graduation_year', 'created_at']


class AlumniEventViewSet(viewsets.ModelViewSet):
    queryset = AlumniEvent.objects.select_related('organizer').all()
    serializer_class = AlumniEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['event_date', 'created_at']


class AlumniDonationViewSet(viewsets.ModelViewSet):
    queryset = AlumniDonation.objects.select_related('donor__user').all()
    serializer_class = AlumniDonationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['donor']
    search_fields = ['purpose', 'receipt_number']
    ordering_fields = ['donation_date', 'amount']
