from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
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

    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        from apps.users.models import User

        total_users = User.objects.filter(is_active=True).count()
        by_role = User.objects.filter(is_active=True).values('role').annotate(
            count=Count('id')
        ).order_by('-count')

        recent_logins = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=24)
        ).count()

        mfa_enabled = User.objects.filter(mfa_enabled=True, is_active=True).count()

        return Response({
            'total_users': total_users,
            'by_role': list(by_role),
            'recent_logins_24h': recent_logins,
            'mfa_enabled': mfa_enabled,
        })

    @action(detail=False, methods=['get'])
    def students_by_lga(self, request):
        from apps.students.models import Student
        from apps.schools.models import School

        stats = Student.objects.filter(status='ACTIVE').values(
            'school__lga'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        return Response(list(stats))

    @action(detail=False, methods=['get'])
    def staff_by_role(self, request):
        from apps.staff.models import Staff

        stats = Staff.objects.filter(is_active=True).values(
            'category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        return Response(list(stats))

    @action(detail=False, methods=['get'])
    def system_status(self, request):
        from django.db import connection
        import os

        db_ok = True
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        except Exception:
            db_ok = False

        storage_used = 0
        storage_total = 1
        try:
            static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
            if os.path.exists(static_dir):
                for dirpath, dirnames, filenames in os.walk(static_dir):
                    for f in filenames:
                        storage_used += os.path.getsize(os.path.join(dirpath, f))
            storage_total = 10 * 1024 * 1024 * 1024  # 10GB assumed
        except Exception:
            pass

        return Response({
            'database': 'online' if db_ok else 'offline',
            'api_server': 'online',
            'storage_used': storage_used,
            'storage_total': storage_total,
            'storage_percent': round((storage_used / storage_total) * 100, 1),
        })

    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        from apps.workflows.models import Task

        overdue = Task.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            due_date__lt=timezone.now()
        ).select_related('workflow_instance', 'assigned_to').order_by('due_date')[:10].values(
            'id', 'workflow_instance__reference_number',
            'assigned_to__first_name', 'assigned_to__last_name',
            'status', 'due_date'
        )

        return Response(list(overdue))

    @action(detail=False, methods=['get'])
    def hr_dashboard(self, request):
        from apps.staff.models import Staff, StaffLeave, StaffPerformance
        from apps.users.models import User

        total_staff = Staff.objects.filter(is_active=True).count()
        by_category = Staff.objects.filter(is_active=True).values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        by_designation = Staff.objects.filter(is_active=True).values('designation').annotate(
            count=Count('id')
        ).order_by('-count')
        by_employment_type = Staff.objects.filter(is_active=True).values('employment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        new_hires_30d = Staff.objects.filter(
            date_joined__gte=timezone.now().date() - timedelta(days=30)
        ).count()
        pending_leaves = StaffLeave.objects.filter(status='PENDING').count()
        approved_leaves = StaffLeave.objects.filter(status='APPROVED').count()
        suspended = Staff.objects.filter(is_suspended=True).count()
        recent_leaves = list(StaffLeave.objects.select_related('staff', 'staff__user').order_by('-created_at')[:5].values(
            'id', 'staff__user__first_name', 'staff__user__last_name',
            'leave_type', 'start_date', 'end_date', 'status'
        ))

        return Response({
            'total_staff': total_staff,
            'by_category': list(by_category),
            'by_designation': list(by_designation),
            'by_employment_type': list(by_employment_type),
            'new_hires_30d': new_hires_30d,
            'pending_leaves': pending_leaves,
            'approved_leaves': approved_leaves,
            'suspended': suspended,
            'recent_leaves': recent_leaves,
        })

    @action(detail=False, methods=['get'])
    def finance_dashboard(self, request):
        from apps.finance.models import Payment, StudentFee, Budget, FeeStructure
        from apps.schools.models import School
        from django.db.models import Sum, Count

        total_collected = Payment.objects.filter(is_confirmed=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_due = StudentFee.objects.filter(status__in=['PENDING', 'PARTIAL']).aggregate(
            total=Sum('balance')
        )['total'] or 0
        collection_rate = (total_collected / (total_collected + total_due) * 100) if (total_collected + total_due) > 0 else 0
        pending_payments = Payment.objects.filter(is_confirmed=False).count()
        payments_today = Payment.objects.filter(payment_date=timezone.now().date()).aggregate(
            total=Sum('amount')
        )['total'] or 0

        collection_by_school = list(
            Payment.objects.filter(is_confirmed=True)
            .values('student_fee__fee_structure__school__name')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')[:10]
        )

        collection_by_method = list(
            Payment.objects.filter(is_confirmed=True)
            .values('payment_method')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )

        budget_summary = list(
            Budget.objects.values('category')
            .annotate(allocated=Sum('allocated_amount'), spent=Sum('spent_amount'))
            .order_by('-allocated')[:10]
        )

        fee_status = list(
            StudentFee.objects.values('status')
            .annotate(count=Count('id'), total=Sum('amount_due'))
        )

        return Response({
            'total_collected': total_collected,
            'total_due': total_due,
            'collection_rate': round(collection_rate, 1),
            'pending_payments': pending_payments,
            'payments_today': payments_today,
            'collection_by_school': collection_by_school,
            'collection_by_method': collection_by_method,
            'budget_summary': budget_summary,
            'fee_status': fee_status,
        })

    @action(detail=False, methods=['get'])
    def principal_dashboard(self, request):
        from apps.schools.models import School
        from apps.students.models import Student
        from apps.staff.models import Staff
        from apps.attendance.models import StudentAttendance
        from datetime import date, timedelta

        user = request.user
        school = None
        staff_profile = getattr(user, 'staff_profile', None)
        if staff_profile and staff_profile.school:
            school = staff_profile.school
        elif user.role in ('SYSADMIN', 'TG_PS'):
            school = School.objects.filter(is_active=True).first()

        if not school:
            return Response({'error': 'No school assigned'}, status=400)

        today = date.today()
        week_ago = today - timedelta(days=7)

        total_students = Student.objects.filter(school=school, status='ACTIVE').count()
        total_staff = Staff.objects.filter(school=school, is_active=True).count()
        male_students = Student.objects.filter(school=school, status='ACTIVE', gender='M').count()
        female_students = total_students - male_students

        attendance_today = StudentAttendance.objects.filter(
            student__school=school, date=today
        )
        attendance_present = attendance_today.filter(status='PRESENT').count()
        attendance_rate = (attendance_present / total_students * 100) if total_students > 0 else 0

        attendance_trend = list(
            StudentAttendance.objects.filter(
                student__school=school, date__gte=week_ago
            ).values('date').annotate(
                present=Count('id', filter=Q(status='PRESENT')),
                total=Count('id')
            ).order_by('date')
        )

        recent_activity = list(
            Staff.objects.filter(school=school, is_active=True)
            .select_related('user')
            .order_by('-updated_at')[:5]
            .values('user__first_name', 'user__last_name', 'designation', 'updated_at')
        )

        # Discipline incidents
        from apps.discipline.models import DisciplinaryIncident
        total_incidents = DisciplinaryIncident.objects.filter(student__school=school).count()
        pending_incidents = DisciplinaryIncident.objects.filter(student__school=school, status='REPORTED').count()
        recent_incidents = list(
            DisciplinaryIncident.objects.filter(student__school=school)
            .select_related('student__user')
            .order_by('-incident_date')[:5]
            .values('id', 'student__user__first_name', 'student__user__last_name', 'incident_type', 'severity', 'status', 'incident_date')
        )

        # Fee collection
        from apps.finance.models import StudentFee, Payment
        from django.db.models import Sum
        total_fees_due = StudentFee.objects.filter(
            student__school=school, status__in=['PENDING', 'PARTIAL']
        ).aggregate(total=Sum('balance'))['total'] or 0
        total_fees_collected = Payment.objects.filter(
            student_fee__student__school=school, is_confirmed=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Pending workflows
        from apps.workflows.models import Task
        pending_tasks = Task.objects.filter(
            assigned_to__staff_profile__school=school,
            status__in=['PENDING', 'IN_PROGRESS']
        ).select_related('workflow_instance').order_by('due_date')[:5].values(
            'id', 'workflow_instance__reference_number', 'status', 'due_date'
        )

        return Response({
            'school_name': school.name,
            'total_students': total_students,
            'total_staff': total_staff,
            'male_students': male_students,
            'female_students': female_students,
            'attendance_rate': round(attendance_rate, 1),
            'attendance_trend': attendance_trend,
            'recent_activity': recent_activity,
            'total_incidents': total_incidents,
            'pending_incidents': pending_incidents,
            'recent_incidents': recent_incidents,
            'total_fees_due': float(total_fees_due),
            'total_fees_collected': float(total_fees_collected),
            'pending_tasks': list(pending_tasks),
        })

    @action(detail=False, methods=['get'])
    def teacher_dashboard(self, request):
        from apps.staff.models import Staff
        from apps.students.models import Student
        from apps.attendance.models import StudentAttendance, StaffAttendance
        from datetime import date, timedelta

        user = request.user
        staff_profile = getattr(user, 'staff_profile', None)
        if not staff_profile:
            return Response({'error': 'No staff profile'}, status=400)

        today = date.today()
        week_ago = today - timedelta(days=7)

        total_students = Student.objects.filter(school=staff_profile.school, status='ACTIVE').count()
        my_students = total_students  # Teachers see their school's students

        attendance_today = StudentAttendance.objects.filter(
            student__school=staff_profile.school, date=today
        )
        present_today = attendance_today.filter(status='PRESENT').count()
        absent_today = attendance_today.filter(status='ABSENT').count()
        attendance_rate = (present_today / total_students * 100) if total_students > 0 else 0

        attendance_trend = list(
            StudentAttendance.objects.filter(
                student__school=staff_profile.school, date__gte=week_ago
            ).values('date').annotate(
                present=Count('id', filter=Q(status='PRESENT')),
                absent=Count('id', filter=Q(status='ABSENT')),
                total=Count('id')
            ).order_by('date')
        )

        # Staff attendance for the school
        staff_present = StaffAttendance.objects.filter(
            staff__school=staff_profile.school, date=today, status='PRESENT'
        ).count()
        total_school_staff = Staff.objects.filter(school=staff_profile.school, is_active=True).count()

        return Response({
            'total_students': my_students,
            'present_today': present_today,
            'absent_today': absent_today,
            'attendance_rate': round(attendance_rate, 1),
            'attendance_trend': attendance_trend,
            'staff_present_today': staff_present,
            'total_school_staff': total_school_staff,
        })

    @action(detail=False, methods=['get'])
    def registry_dashboard(self, request):
        from apps.files.models import File, FileMovement
        from apps.workflows.models import WorkflowInstance, Task

        total_files = File.objects.count()
        active_files = File.objects.filter(status='ACTIVE').count()
        pending_files = File.objects.filter(status='PENDING').count()
        archived_files = File.objects.filter(status='ARCHIVED').count()

        files_by_status = list(
            File.objects.values('status').annotate(count=Count('id')).order_by('status')
        )

        recent_movements = list(
            FileMovement.objects.select_related('file', 'from_holder', 'to_holder')
            .order_by('-movement_date')[:10]
            .values(
                'file__file_number', 'file__title', 'from_holder__first_name',
                'to_holder__first_name', 'action', 'movement_date'
            )
        )

        pending_workflows = WorkflowInstance.objects.filter(status='PENDING').count()
        active_workflows = WorkflowInstance.objects.filter(status='IN_PROGRESS').count()
        overdue_tasks = Task.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'], due_date__lt=timezone.now()
        ).count()

        return Response({
            'total_files': total_files,
            'active_files': active_files,
            'pending_files': pending_files,
            'archived_files': archived_files,
            'files_by_status': files_by_status,
            'recent_movements': recent_movements,
            'pending_workflows': pending_workflows,
            'active_workflows': active_workflows,
            'overdue_tasks': overdue_tasks,
        })

    @action(detail=False, methods=['get'])
    def parent_dashboard(self, request):
        from apps.students.models import Student
        from apps.finance.models import StudentFee, Payment
        from django.db.models import Sum

        user = request.user
        children = Student.objects.filter(parents__user=user, status='ACTIVE').select_related('school', 'class_name').distinct()

        children_data = []
        for child in children:
            fees = StudentFee.objects.filter(student=child)
            total_due = fees.aggregate(total=Sum('amount_due'))['total'] or 0
            total_paid = fees.aggregate(total=Sum('amount_paid'))['total'] or 0
            balance = total_due - total_paid
            recent_payments = list(
                Payment.objects.filter(student_fee__student=child, is_confirmed=True)
                .order_by('-payment_date')[:3]
                .values('amount', 'payment_date', 'payment_method', 'reference_number')
            )
            children_data.append({
                'id': child.id,
                'name': child.user.get_full_name(),
                'admission_number': child.admission_number,
                'school': child.school.name if child.school else '',
                'class_name': child.class_name.name if child.class_name else '',
                'total_due': total_due,
                'total_paid': total_paid,
                'balance': balance,
                'recent_payments': recent_payments,
            })

        return Response({
            'children': children_data,
            'total_children': len(children_data),
        })
