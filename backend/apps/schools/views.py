from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import School, SchoolAcademicYear
from .serializers import SchoolSerializer, SchoolListSerializer, SchoolAcademicYearSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.select_related('principal', 'vice_principal').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_type', 'lga', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SchoolListSerializer
        return SchoolSerializer


class SchoolAcademicYearViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolAcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SchoolAcademicYear.objects.filter(school_id=self.kwargs['school_pk'])
    
    def perform_create(self, serializer):
        serializer.save(school_id=self.kwargs['school_pk'])
