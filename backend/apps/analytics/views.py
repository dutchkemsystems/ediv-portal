from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import AnalyticsReport, KPI
from .serializers import AnalyticsReportSerializer, KPISerializer


class AnalyticsReportViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsReport.objects.select_related('generated_by').all()
    serializer_class = AnalyticsReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'is_scheduled', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'last_generated']


class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['metric_type', 'academic_year', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class DashboardStatsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        from apps.schools.models import School
        from apps.students.models import Student
        from apps.staff.models import Staff
        from apps.files.models import File
        
        stats = {
            'total_schools': School.objects.filter(is_active=True).count(),
            'total_students': Student.objects.filter(status='ACTIVE').count(),
            'total_staff': Staff.objects.filter(is_active=True).count(),
            'total_files': File.objects.exclude(status='ARCHIVED').count(),
            'active_files': File.objects.filter(status='ACTIVE').count(),
            'pending_files': File.objects.filter(status='PENDING').count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def school_stats(self, request):
        from apps.schools.models import School
        from django.db.models import Count
        
        schools = School.objects.filter(is_active=True).annotate(
            student_count=Count('students'),
            staff_count=Count('staff')
        ).values('id', 'name', 'code', 'school_type', 'lga', 'student_count', 'staff_count')
        
        return Response(list(schools))
    
    @action(detail=False, methods=['get'])
    def enrollment_stats(self, request):
        from apps.students.models import Student
        from apps.schools.models import School
        from django.db.models import Count
        
        stats = Student.objects.filter(status='ACTIVE').values('school__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(list(stats))
    
    @action(detail=False, methods=['get'])
    def attendance_stats(self, request):
        from apps.attendance.models import StudentAttendance
        from django.db.models import Count
        from datetime import date, timedelta
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        stats = StudentAttendance.objects.filter(
            date__gte=week_ago
        ).values('status').annotate(
            count=Count('id')
        )
        
        return Response(list(stats))
    
    @action(detail=False, methods=['get'])
    def financial_stats(self, request):
        from apps.finance.models import Payment, StudentFee
        from django.db.models import Sum
        
        total_collected = Payment.objects.filter(is_confirmed=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_due = StudentFee.objects.filter(status__in=['PENDING', 'PARTIAL']).aggregate(
            total=Sum('balance')
        )['total'] or 0
        
        return Response({
            'total_collected': total_collected,
            'total_due': total_due,
            'collection_rate': (total_collected / (total_collected + total_due) * 100) if (total_collected + total_due) > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        from apps.files.models import FileMovement
        from apps.workflows.models import Task
        
        recent_files = FileMovement.objects.select_related(
            'file', 'from_holder', 'to_holder'
        ).order_by('-movement_date')[:10].values(
            'file__file_number', 'file__title', 'from_holder__first_name',
            'to_holder__first_name', 'action', 'movement_date'
        )
        
        recent_tasks = Task.objects.select_related(
            'workflow_instance', 'assigned_to'
        ).filter(status__in=['PENDING', 'IN_PROGRESS']).order_by('-created_at')[:10].values(
            'workflow_instance__reference_number', 'assigned_to__first_name',
            'status', 'due_date'
        )
        
        return Response({
            'recent_files': list(recent_files),
            'recent_tasks': list(recent_tasks)
        })
