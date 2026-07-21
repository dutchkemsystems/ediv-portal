from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CPDActivity, CPDEnrollment, CPDRecord
from .serializers import CPDActivitySerializer, CPDEnrollmentSerializer, CPDRecordSerializer


class CPDActivityViewSet(viewsets.ModelViewSet):
    queryset = CPDActivity.objects.all()
    serializer_class = CPDActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['training_type', 'status', 'is_mandatory']
    search_fields = ['title', 'description', 'provider']
    ordering_fields = ['start_date', 'created_at']


class CPDEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CPDEnrollment.objects.select_related('activity', 'staff__user').all()
    serializer_class = CPDEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activity', 'staff']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    ordering_fields = ['enrollment_date', 'created_at']


class CPDRecordViewSet(viewsets.ModelViewSet):
    queryset = CPDRecord.objects.select_related('staff__user').all()
    serializer_class = CPDRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['staff', 'academic_year', 'is_compliant']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    ordering_fields = ['academic_year', 'created_at']
