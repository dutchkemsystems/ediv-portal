from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.predictive_analytics.models import StudentRiskProfile, EarlyWarningAlert, RiskTrend
from apps.predictive_analytics.services.prediction_engine import DropoutPredictionEngine


class Command(BaseCommand):
    help = 'Run AI dropout prediction analysis for all active students'

    def add_arguments(self, parser):
        parser.add_argument('--student-id', type=int, help='Analyze a specific student by ID')
        parser.add_argument('--threshold', type=str, default='MEDIUM',
                          help='Minimum risk level to create alerts (LOW/MEDIUM/HIGH/CRITICAL)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting dropout prediction analysis...'))

        if options['student_id']:
            from apps.students.models import Student
            try:
                student = Student.objects.get(id=options['student_id'])
            except Student.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Student {options["student_id"]} not found'))
                return

            analysis = DropoutPredictionEngine.analyze_student(student)
            profile, _ = StudentRiskProfile.objects.update_or_create(
                student=student,
                defaults={**analysis, 'last_analyzed': timezone.now()}
            )
            RiskTrend.objects.create(student=student, **{
                'risk_score': analysis['risk_score'],
                'risk_level': analysis['risk_level'],
                'attendance_risk': analysis['attendance_risk'],
                'academic_risk': analysis['academic_risk'],
                'discipline_risk': analysis['discipline_risk'],
                'financial_risk': analysis['financial_risk'],
            })
            self.stdout.write(self.style.SUCCESS(
                f'{student} - Risk: {analysis["risk_level"]} ({analysis["risk_score"]:.1f}%)'
            ))
            return

        results = DropoutPredictionEngine.analyze_all_students()
        saved = 0
        alerts_created = 0

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
            RiskTrend.objects.create(student_id=r['student_id'], **{
                'risk_score': r['risk_score'],
                'risk_level': r['risk_level'],
                'attendance_risk': r['attendance_risk'],
                'academic_risk': r['academic_risk'],
                'discipline_risk': r['discipline_risk'],
                'financial_risk': r['financial_risk'],
            })
            saved += 1

            if r['risk_level'] in ('HIGH', 'CRITICAL'):
                alert, created = EarlyWarningAlert.objects.get_or_create(
                    student_id=r['student_id'],
                    alert_type='DROPOUT_RISK',
                    risk_level=r['risk_level'],
                    defaults={
                        'risk_profile': profile,
                        'message': f"Student at {r['risk_level']} risk (score: {r['risk_score']:.1f}%)",
                        'details': {'risk_factors': r['risk_factors']},
                    }
                )
                if created:
                    alerts_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Analysis complete: {saved} students analyzed, {alerts_created} new alerts created.'
        ))
