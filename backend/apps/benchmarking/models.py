from django.db import models


class BenchmarkMetric(models.Model):
    CATEGORY_CHOICES = [
        ('ACADEMIC', 'Academic Performance'),
        ('ATTENDANCE', 'Attendance'),
        ('FINANCIAL', 'Financial'),
        ('STAFF', 'Staff Performance'),
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('EXTRACURRICULAR', 'Extra-Curricular'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, blank=True)
    higher_is_better = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'benchmark_metrics'

    def __str__(self):
        return self.name


class SchoolBenchmark(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE,
                              related_name='benchmarks')
    metric = models.ForeignKey(BenchmarkMetric, on_delete=models.CASCADE,
                              related_name='school_benchmarks')
    value = models.FloatField()
    period = models.CharField(max_length=20)  # e.g., '2025/2026', 'Term 1'
    academic_session = models.CharField(max_length=20, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'school_benchmarks'
        unique_together = ['school', 'metric', 'period']
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.school.name} - {self.metric.name}: {self.value}"


class BenchmarkComparison(models.Model):
    school_a = models.ForeignKey('schools.School', on_delete=models.CASCADE,
                                related_name='comparisons_as_a')
    school_b = models.ForeignKey('schools.School', on_delete=models.CASCADE,
                                related_name='comparisons_as_b')
    metric = models.ForeignKey(BenchmarkMetric, on_delete=models.CASCADE)
    value_a = models.FloatField()
    value_b = models.FloatField()
    difference = models.FloatField()
    percentage_difference = models.FloatField()
    period = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'benchmark_comparisons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.school_a.name} vs {self.school_b.name} - {self.metric.name}"
