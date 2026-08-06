from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import date

from .models import StudentRiskProfile, EarlyWarningAlert, Intervention, RiskTrend
from .serializers import (
    StudentRiskProfileSerializer, EarlyWarningAlertSerializer,
    InterventionSerializer, RiskTrendSerializer
)
from .services.prediction_engine import DropoutPredictionEngine


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('SYSADMIN', 'TG_PS', 'QA')


class StudentRiskProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentRiskProfile.objects.all()
    serializer_class = StudentRiskProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['risk_level']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['risk_score', 'last_analyzed']

    @action(detail=False, methods=['post'], url_path='analyze-all')
    def analyze_all(self, request):
        results = DropoutPredictionEngine.analyze_all_students()
        saved = 0
        for r in results:
            profile, _ = StudentRiskProfile.objects.update_or_create(
                student_id=r['student_id'],
                defaults={
                    'risk_score': r['risk_score'],
                    'risk_level': r['risk_level'],
                    'attendance_risk': r['attendance_risk'],
                    'academic_risk': r['academic_risk'],
                    'discipline_risk': r['discipline_risk'],
                    'financial_risk': r['financial_risk'],
                    'engagement_risk': r['engagement_risk'],
                    'risk_factors': r['risk_factors'],
                    'recommendations': r['recommendations'],
                    'last_analyzed': timezone.now(),
                }
            )
            RiskTrend.objects.create(
                student_id=r['student_id'],
                risk_score=r['risk_score'],
                risk_level=r['risk_level'],
                attendance_risk=r['attendance_risk'],
                academic_risk=r['academic_risk'],
                discipline_risk=r['discipline_risk'],
                financial_risk=r['financial_risk'],
            )
            if r['risk_level'] in ('HIGH', 'CRITICAL'):
                EarlyWarningAlert.objects.update_or_create(
                    student_id=r['student_id'],
                    alert_type='DROPOUT_RISK',
                    risk_level=r['risk_level'],
                    defaults={
                        'risk_profile': profile,
                        'message': f"Student at {r['risk_level']} risk of dropping out (score: {r['risk_score']:.1f}%).",
                        'details': {'risk_factors': r['risk_factors']},
                    }
                )
            saved += 1
        return Response({'message': f'Analyzed {saved} students.', 'results_count': len(results)})

    @action(detail=True, methods=['post'], url_path='analyze')
    def analyze_single(self, request, pk=None):
        profile = self.get_object()
        from apps.students.models import Student
        try:
            student = Student.objects.get(id=profile.student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        analysis = DropoutPredictionEngine.analyze_student(student)
        profile.risk_score = analysis['risk_score']
        profile.risk_level = analysis['risk_level']
        profile.attendance_risk = analysis['attendance_risk']
        profile.academic_risk = analysis['academic_risk']
        profile.discipline_risk = analysis['discipline_risk']
        profile.financial_risk = analysis['financial_risk']
        profile.engagement_risk = analysis['engagement_risk']
        profile.risk_factors = analysis['risk_factors']
        profile.recommendations = analysis['recommendations']
        profile.last_analyzed = timezone.now()
        profile.save()

        return Response(StudentRiskProfileSerializer(profile).data)

    @action(detail=False, methods=['get'], url_path='summary')
    def risk_summary(self, request):
        profiles = StudentRiskProfile.objects.all()
        summary = {
            'total_students': profiles.count(),
            'by_level': {
                'CRITICAL': profiles.filter(risk_level='CRITICAL').count(),
                'HIGH': profiles.filter(risk_level='HIGH').count(),
                'MEDIUM': profiles.filter(risk_level='MEDIUM').count(),
                'LOW': profiles.filter(risk_level='LOW').count(),
            },
            'top_risk_factors': self._get_top_factors(profiles),
            'needs_intervention': profiles.filter(risk_level__in=['HIGH', 'CRITICAL']).count(),
        }
        return Response(summary)

    @action(detail=False, methods=['get'], url_path='trends')
    def risk_trends(self, request):
        from django.db.models import Avg
        trends = RiskTrend.objects.values('snapshot_date').annotate(
            avg_score=Avg('risk_score')
        ).order_by('snapshot_date')[:30]
        return Response(list(trends))

    def _get_top_factors(self, profiles):
        factor_counts = {}
        for p in profiles:
            for f in p.risk_factors:
                cat = f.get('category', 'unknown')
                factor_counts[cat] = factor_counts.get(cat, 0) + 1
        return sorted(factor_counts.items(), key=lambda x: -x[1])[:5]


class EarlyWarningAlertViewSet(viewsets.ModelViewSet):
    queryset = EarlyWarningAlert.objects.all()
    serializer_class = EarlyWarningAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['alert_type', 'risk_level', 'acknowledged']
    ordering_fields = ['-created_at']

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_alert(self, request, pk=None):
        alert = self.get_object()
        alert.acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response({'message': 'Alert acknowledged.'})


class InterventionViewSet(viewsets.ModelViewSet):
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'intervention_type']
    ordering_fields = ['-created_at']

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_intervention(self, request, pk=None):
        intervention = self.get_object()
        intervention.status = 'COMPLETED'
        intervention.outcome = request.data.get('outcome', '')
        intervention.completed_at = timezone.now()
        intervention.save()
        return Response({'message': 'Intervention marked as completed.'})


class RiskTrendViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskTrend.objects.all()
    serializer_class = RiskTrendSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'risk_level']
