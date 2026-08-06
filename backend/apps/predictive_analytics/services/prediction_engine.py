import datetime
import logging
from django.db.models import Q, Avg, Count, F
from django.utils import timezone

logger = logging.getLogger('apps')


class DropoutPredictionEngine:
    """Multi-factor risk assessment engine for student dropout prediction."""

    WEIGHTS = {
        'attendance': 0.30,
        'academic': 0.25,
        'discipline': 0.15,
        'financial': 0.20,
        'engagement': 0.10,
    }

    THRESHOLDS = {
        'LOW': 25,
        'MEDIUM': 50,
        'HIGH': 75,
        'CRITICAL': 90,
    }

    @classmethod
    def analyze_student(cls, student):
        """Full risk analysis for a single student."""
        scores = {
            'attendance': cls._attendance_risk(student),
            'academic': cls._academic_risk(student),
            'discipline': cls._discipline_risk(student),
            'financial': cls._financial_risk(student),
            'engagement': cls._engagement_risk(student),
        }

        risk_score = sum(
            scores[k] * cls.WEIGHTS[k] for k in scores
        )

        risk_level = cls._score_to_level(risk_score)
        risk_factors = cls._identify_factors(student, scores)
        recommendations = cls._generate_recommendations(student, scores, risk_level)

        return {
            'risk_score': round(min(risk_score, 100), 1),
            'risk_level': risk_level,
            'attendance_risk': round(scores['attendance'], 1),
            'academic_risk': round(scores['academic'], 1),
            'discipline_risk': round(scores['discipline'], 1),
            'financial_risk': round(scores['financial'], 1),
            'engagement_risk': round(scores['engagement'], 1),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
        }

    @classmethod
    def _attendance_risk(cls, student):
        """Risk from attendance patterns: absence rate, streaks, trends."""
        try:
            from apps.attendance.models import StudentAttendance
            today = datetime.date.today()
            ninety_days_ago = today - datetime.timedelta(days=90)
            thirty_days_ago = today - datetime.timedelta(days=30)

            recent = StudentAttendance.objects.filter(
                student=student,
                date__gte=ninety_days_ago
            )
            if not recent.exists():
                return 20.0

            total = recent.count()
            absent = recent.filter(status='ABSENT').count()
            late = recent.filter(status='LATE').count()

            absence_rate = (absent / total) * 100 if total > 0 else 0
            lateness_rate = (late / total) * 100 if total > 0 else 0

            last_30 = recent.filter(date__gte=thirty_days_ago)
            recent_absent = last_30.filter(status='ABSENT').count()
            recent_total = last_30.count()
            recent_rate = (recent_absent / recent_total) * 100 if recent_total > 0 else 0

            streak = cls._max_absence_streak(recent.order_by('date'))

            score = 0
            score += min(absence_rate * 1.2, 40)
            score += min(lateness_rate * 0.5, 15)
            if recent_rate > 30:
                score += 25
            elif recent_rate > 15:
                score += 15
            if streak >= 5:
                score += 25
            elif streak >= 3:
                score += 15

            return min(score, 100)
        except Exception as e:
            logger.warning(f'Attendance risk calculation failed for {student}: {e}')
            return 0.0

    @classmethod
    def _academic_risk(cls, student):
        """Risk from grade trends: declining scores, failures, low averages."""
        try:
            from apps.academics.models import ExamResult
            results = ExamResult.objects.filter(
                student=student
            ).order_by('-exam__exam_date')[:10]

            if not results.exists():
                return 15.0

            scores = list(results.values_list('score', flat=True))
            if not scores:
                return 15.0

            avg = sum(scores) / len(scores)
            recent_avg = sum(scores[:3]) / min(len(scores), 3) if scores[:3] else avg

            score = 0
            if avg < 40:
                score += 40
            elif avg < 50:
                score += 25
            elif avg < 60:
                score += 10

            if len(scores) >= 3 and recent_avg < avg - 10:
                score += 25
            elif len(scores) >= 3 and recent_avg < avg - 5:
                score += 15

            failures = sum(1 for s in scores if s < 40)
            score += min(failures * 8, 30)

            return min(score, 100)
        except Exception as e:
            logger.warning(f'Academic risk calculation failed for {student}: {e}')
            return 0.0

    @classmethod
    def _discipline_risk(cls, student):
        """Risk from disciplinary records."""
        try:
            from apps.discipline.models import DisciplinaryIncident
            year_start = datetime.date(datetime.date.today().year, 1, 1)
            incidents = DisciplinaryIncident.objects.filter(
                student=student,
                incident_date__gte=year_start
            )
            count = incidents.count()
            serious = incidents.filter(
                severity__in=['HIGH', 'CRITICAL']
            ).count()

            score = 0
            score += min(count * 5, 30)
            score += min(serious * 15, 50)
            return min(score, 100)
        except Exception:
            return 0.0

    @classmethod
    def _financial_risk(cls, student):
        """Risk from fee payment patterns."""
        try:
            from apps.finance.models import StudentFee
            fees = StudentFee.objects.filter(student=student)
            if not fees.exists():
                return 0.0

            total_due = sum(f.amount_due for f in fees)
            total_paid = sum(f.amount_paid for f in fees)

            if total_due == 0:
                return 0.0

            outstanding = ((total_due - total_paid) / total_due) * 100
            overdue = fees.filter(
                due_date__lt=datetime.date.today(),
                amount_paid__lt=F('amount_due')
            ).count()

            score = 0
            score += min(outstanding * 0.6, 40)
            score += min(overdue * 15, 45)
            return min(score, 100)
        except Exception:
            return 0.0

    @classmethod
    def _engagement_risk(cls, student):
        """Risk from participation in activities."""
        try:
            from apps.attendance.models import StudentAttendance
            from apps.co_curricular.models import ActivityParticipant

            today = datetime.date.today()
            term_start = today - datetime.timedelta(days=120)

            activities = ActivityParticipant.objects.filter(
                student=student,
                joined_date__gte=term_start
            ).count()

            score = 0
            if activities == 0:
                score += 40

            return min(score, 100)
        except Exception:
            return 0.0

    @classmethod
    def _max_absence_streak(cls, attendance_qs):
        max_streak = 0
        current_streak = 0
        for att in attendance_qs:
            if att.status == 'ABSENT':
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        return max_streak

    @classmethod
    def _score_to_level(cls, score):
        if score >= cls.THRESHOLDS['CRITICAL']:
            return 'CRITICAL'
        elif score >= cls.THRESHOLDS['HIGH']:
            return 'HIGH'
        elif score >= cls.THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        return 'LOW'

    @classmethod
    def _identify_factors(cls, student, scores):
        factors = []
        if scores['attendance'] > 40:
            factors.append({'factor': 'High absence rate', 'score': scores['attendance'], 'category': 'attendance'})
        if scores['academic'] > 40:
            factors.append({'factor': 'Declining grades', 'score': scores['academic'], 'category': 'academic'})
        if scores['discipline'] > 30:
            factors.append({'factor': 'Discipline issues', 'score': scores['discipline'], 'category': 'discipline'})
        if scores['financial'] > 40:
            factors.append({'factor': 'Outstanding fees', 'score': scores['financial'], 'category': 'financial'})
        if scores['engagement'] > 30:
            factors.append({'factor': 'Low participation', 'score': scores['engagement'], 'category': 'engagement'})
        return factors

    @classmethod
    def _generate_recommendations(cls, student, scores, risk_level):
        recs = []
        if scores['attendance'] > 40:
            recs.append({
                'action': 'Schedule parent meeting to discuss attendance',
                'priority': 'HIGH' if scores['attendance'] > 60 else 'MEDIUM',
                'department': 'ADMIN_HR',
            })
        if scores['academic'] > 40:
            recs.append({
                'action': 'Assign peer tutor or extra lessons',
                'priority': 'HIGH' if scores['academic'] > 60 else 'MEDIUM',
                'department': 'QA',
            })
        if scores['discipline'] > 30:
            recs.append({
                'action': 'Refer to school counselor',
                'priority': 'HIGH',
                'department': 'CC',
            })
        if scores['financial'] > 40:
            recs.append({
                'action': 'Review fee payment plan or financial aid',
                'priority': 'MEDIUM',
                'department': 'FIN',
            })
        if risk_level == 'CRITICAL':
            recs.append({
                'action': 'Emergency intervention meeting with all stakeholders',
                'priority': 'CRITICAL',
                'department': 'ADMIN_HR',
            })
        return recs

    @classmethod
    def analyze_all_students(cls):
        """Batch analysis for all active students."""
        from apps.students.models import Student
        students = Student.objects.filter(is_active=True)
        results = []
        for student in students:
            try:
                analysis = cls.analyze_student(student)
                results.append({'student_id': student.id, **analysis})
            except Exception as e:
                logger.error(f'Failed to analyze student {student.id}: {e}')
        return results
