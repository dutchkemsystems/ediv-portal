from django.db.models import Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from ..models import BenchmarkMetric, SchoolBenchmark, BenchmarkComparison


class BenchmarkingService:
    @staticmethod
    def calculate_school_metrics(school_id, period=None):
        if not period:
            period = timezone.now().strftime('%Y/%Y')

        from apps.students.models import Student, AcademicRecord
        from apps.attendance.models import Attendance
        from apps.finance.models import FeeBalance

        school_students = Student.objects.filter(school_id=school_id)

        metrics = {}

        avg_score = AcademicRecord.objects.filter(
            student__school_id=school_id
        ).aggregate(avg=Avg('score'))['avg'] or 0
        metrics['AVG_SCORE'] = avg_score

        total = Attendance.objects.filter(student__school_id=school_id).count()
        present = Attendance.objects.filter(student__school_id=school_id, status='PRESENT').count()
        metrics['ATTENDANCE_RATE'] = (present / total * 100) if total > 0 else 0

        total_fees = FeeBalance.objects.filter(student__school_id=school_id).aggregate(
            total=Avg('amount_owed'))['total'] or 0
        paid_fees = FeeBalance.objects.filter(student__school_id=school_id).aggregate(
            total=Avg('amount_paid'))['total'] or 0
        metrics['FEE_COLLECTION_RATE'] = (paid_fees / total_fees * 100) if total_fees > 0 else 0

        metrics['STUDENT_TEACHER_RATIO'] = (
            school_students.count() / 25  # Placeholder
        )

        for code, value in metrics.items():
            metric = BenchmarkMetric.objects.filter(code=code).first()
            if metric:
                SchoolBenchmark.objects.update_or_create(
                    school_id=school_id, metric=metric, period=period,
                    defaults={'value': value}
                )

        return metrics

    @staticmethod
    def compare_schools(school_a_id, school_b_id, metric_code=None):
        metrics = BenchmarkMetric.objects.all()
        if metric_code:
            metrics = metrics.filter(code=metric_code)

        comparisons = []
        for metric in metrics:
            bench_a = SchoolBenchmark.objects.filter(
                school_id=school_a_id, metric=metric
            ).order_by('-calculated_at').first()
            bench_b = SchoolBenchmark.objects.filter(
                school_id=school_b_id, metric=metric
            ).order_by('-calculated_at').first()

            if bench_a and bench_b:
                diff = bench_a.value - bench_b.value
                pct_diff = (diff / bench_b.value * 100) if bench_b.value != 0 else 0

                comparison, _ = BenchmarkComparison.objects.update_or_create(
                    school_a_id=school_a_id, school_b_id=school_b_id,
                    metric=metric, period=bench_a.period,
                    defaults={
                        'value_a': bench_a.value,
                        'value_b': bench_b.value,
                        'difference': diff,
                        'percentage_difference': pct_diff,
                    }
                )
                comparisons.append({
                    'metric': metric.name,
                    'category': metric.category,
                    'school_a_value': bench_a.value,
                    'school_b_value': bench_b.value,
                    'difference': round(diff, 2),
                    'percentage_difference': round(pct_diff, 2),
                    'unit': metric.unit,
                })

        return comparisons

    @staticmethod
    def get_district_rankings(metric_code, period=None):
        metric = BenchmarkMetric.objects.filter(code=metric_code).first()
        if not metric:
            return []

        benchmarks = SchoolBenchmark.objects.filter(
            metric=metric
        ).select_related('school')

        if period:
            benchmarks = benchmarks.filter(period=period)

        rankings = []
        sorted_benchmarks = sorted(
            benchmarks, key=lambda x: x.value,
            reverse=metric.higher_is_better
        )

        for i, b in enumerate(sorted_benchmarks, 1):
            rankings.append({
                'rank': i,
                'school_id': b.school_id,
                'school_name': b.school.name,
                'value': b.value,
                'unit': metric.unit,
                'period': b.period,
            })

        return rankings

    @staticmethod
    def get_school_performance_summary(school_id):
        benchmarks = SchoolBenchmark.objects.filter(
            school_id=school_id
        ).select_related('metric').order_by('-calculated_at')

        summary = {}
        for b in benchmarks:
            if b.metric.code not in summary:
                summary[b.metric.code] = {
                    'metric': b.metric.name,
                    'category': b.metric.category,
                    'value': b.value,
                    'unit': b.metric.unit,
                    'period': b.period,
                }

        return summary

    @staticmethod
    def get_top_performing_schools(metric_code, limit=10):
        metric = BenchmarkMetric.objects.filter(code=metric_code).first()
        if not metric:
            return []

        benchmarks = SchoolBenchmark.objects.filter(
            metric=metric
        ).select_related('school').order_by(
            '-value' if metric.higher_is_better else 'value'
        )[:limit]

        return [{
            'school_id': b.school_id,
            'school_name': b.school.name,
            'value': b.value,
            'unit': metric.unit,
        } for b in benchmarks]
