from django.db import models
from django.conf import settings


class MeetingType(models.TextChoices):
    PARENT_TEACHER = 'PARENT_TEACHER', 'Parent-Teacher Conference'
    PROGRESS_REVIEW = 'PROGRESS_REVIEW', 'Progress Review'
    DISCIPLINARY = 'DISCIPLINARY', 'Disciplinary Meeting'
    ACADEMIC_SUPPORT = 'ACADEMIC_SUPPORT', 'Academic Support'
    CAREER_GUIDANCE = 'CAREER_GUIDANCE', 'Career Guidance'
    GENERAL = 'GENERAL', 'General Meeting'


class MeetingStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    RESCHEDULED = 'RESCHEDULED', 'Rescheduled'


class PTAMeeting(models.Model):
    title = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices)
    description = models.TextField(blank=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='pta_meetings')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    venue = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=MeetingStatus.choices, default='SCHEDULED')
    organized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='organized_pta_meetings'
    )
    attendees_parents = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='pta_attendees')
    minutes = models.TextField(blank=True)
    decisions = models.TextField(blank=True)
    follow_up_actions = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.school.name} ({self.scheduled_date})"


class MessageCategory(models.TextChoices):
    ACADEMIC = 'ACADEMIC', 'Academic Update'
    BEHAVIOR = 'BEHAVIOR', 'Behavior Update'
    ATTENDANCE = 'ATTENDANCE', 'Attendance'
    EVENTS = 'EVENTS', 'School Events'
    FEES = 'FEES', 'Fees & Payments'
    GENERAL = 'GENERAL', 'General'
    URGENT = 'URGENT', 'Urgent'


class ParentTeacherMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pt_sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pt_received_messages'
    )
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='pt_messages')
    category = models.CharField(max_length=15, choices=MessageCategory.choices, default='GENERAL')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    parent_reply = models.TextField(blank=True)
    parent_replied_at = models.DateTimeField(null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.subject}"


class ReportShareType(models.TextChoices):
    PROGRESS_REPORT = 'PROGRESS_REPORT', 'Progress Report'
    ATTENDANCE_REPORT = 'ATTENDANCE_REPORT', 'Attendance Report'
    BEHAVIOR_REPORT = 'BEHAVIOR_REPORT', 'Behavior Report'
    EXAM_RESULTS = 'EXAM_RESULTS', 'Exam Results'
    REPORT_CARD = 'REPORT_CARD', 'Report Card'


class StudentReportShare(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='shared_reports')
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_student_reports'
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_student_reports'
    )
    report_type = models.CharField(max_length=20, choices=ReportShareType.choices)
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, blank=True)
    comments = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} - {self.student} ({self.academic_year})"
