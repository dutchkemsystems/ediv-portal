from django.db import models
from django.conf import settings


class PointCategory(models.Model):
    ACTION_CHOICES = [
        ('ATTENDANCE', 'Perfect Attendance'),
        ('ACADEMIC', 'Academic Excellence'),
        ('ASSIGNMENT', 'Assignment Submission'),
        ('PARTICIPATION', 'Class Participation'),
        ('LEADERSHIP', 'Leadership'),
        ('COMMUNITY', 'Community Service'),
        ('PROFESSIONAL', 'Professional Development'),
        ('ADMINISTRATIVE', 'Administrative Efficiency'),
        ('INNOVATION', 'Innovation'),
        ('MENTORING', 'Mentoring'),
    ]

    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, unique=True)
    points = models.IntegerField(default=10)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    daily_limit = models.IntegerField(default=0, help_text='0 = unlimited')

    class Meta:
        db_table = 'point_categories'

    def __str__(self):
        return f"{self.name} ({self.points} pts)"


class Badge(models.Model):
    TIER_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏅')
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='BRONZE')
    points_required = models.IntegerField(default=0)
    category = models.ForeignKey(PointCategory, on_delete=models.SET_NULL, null=True, blank=True)
    criteria = models.JSONField(default=dict, help_text='Auto-award criteria JSON')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'badges'
        ordering = ['points_required']

    def __str__(self):
        return f"{self.icon} {self.name} ({self.tier})"


class UserPoints(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='gamification_points')
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_points'

    def __str__(self):
        return f"{self.user.email} - Level {self.level} ({self.total_points} pts)"

    def calculate_level(self):
        thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500,
                      5500, 6600, 7800, 9100, 10500, 12000, 13600, 15300, 17100, 19000]
        for i, threshold in enumerate(reversed(thresholds)):
            if self.total_points >= threshold:
                return len(thresholds) - i
        return 1


class PointTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='point_transactions')
    category = models.ForeignKey(PointCategory, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    reference_model = models.CharField(max_length=50, blank=True)
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='awarded_points')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'point_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}: +{self.points} ({self.category.name})"


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


class Leaderboard(models.Model):
    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('TERM', 'Term'),
        ('ALL_TIME', 'All Time'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    points_earned = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'leaderboards'
        unique_together = ['user', 'period', 'period_start']
        ordering = ['-points_earned']

    def __str__(self):
        return f"{self.user.email} - {self.period} ({self.rank})"
