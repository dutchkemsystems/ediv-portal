from django.db import models
from django.conf import settings


class ReportCardTemplate(models.Model):
    name = models.CharField(max_length=200)
    school_type = models.CharField(max_length=50, blank=True)
    header_text = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    include_photo = models.BooleanField(default=True)
    include_signature = models.BooleanField(default=True)
    include_remarks = models.BooleanField(default=True)
    include_class_average = models.BooleanField(default=True)
    include_position = models.BooleanField(default=True)
    custom_fields = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_card_templates'

    def __str__(self):
        return self.name


class GeneratedReportCard(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE,
                               related_name='generated_report_cards')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    template = models.ForeignKey(ReportCardTemplate, on_delete=models.SET_NULL, null=True)
    academic_session = models.CharField(max_length=20)
    term = models.CharField(max_length=20)

    # Results
    total_score = models.FloatField(default=0)
    average_score = models.FloatField(default=0)
    class_average = models.FloatField(default=0)
    position = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(default=0)
    remark = models.TextField(blank=True)
    teacher_remark = models.TextField(blank=True)
    principal_remark = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    pdf_file = models.FileField(upload_to='report_cards/', blank=True, null=True)
    error_message = models.TextField(blank=True)

    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, related_name='generated_report_cards')
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'generated_report_cards'
        unique_together = ['student', 'academic_session', 'term']
        ordering = ['-created_at']

    def __str__(self):
        return f"Report Card: {self.student} - {self.term} {self.academic_session}"


class ReportCardShareLog(models.Model):
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('WHATSAPP', 'WhatsApp'),
        ('SMS', 'SMS'),
        ('DOWNLOAD', 'Download'),
        ('PRINT', 'Print'),
    ]

    report_card = models.ForeignKey(GeneratedReportCard, on_delete=models.CASCADE,
                                   related_name='share_logs')
    channel = models.CharField(max_length=15, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=200)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                  null=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='SENT')

    class Meta:
        db_table = 'report_card_share_logs'
        ordering = ['-shared_at']

    def __str__(self):
        return f"{self.report_card} shared via {self.channel}"
