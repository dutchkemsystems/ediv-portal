from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import (
    PointCategory, Badge, UserPoints, PointTransaction,
    UserBadge, Leaderboard
)


class GamificationEngine:
    @staticmethod
    def award_points(user, action_type, description='', reference_id='', reference_model='', awarded_by=None):
        category = PointCategory.objects.filter(action_type=action_type, is_active=True).first()
        if not category:
            return None

        if category.daily_limit > 0:
            today = timezone.now().date()
            today_count = PointTransaction.objects.filter(
                user=user, category=category,
                created_at__date=today
            ).count()
            if today_count >= category.daily_limit:
                return None

        transaction = PointTransaction.objects.create(
            user=user, category=category, points=category.points,
            description=description, reference_id=reference_id,
            reference_model=reference_model, awarded_by=awarded_by
        )

        user_points, _ = UserPoints.objects.get_or_create(user=user)
        user_points.total_points += category.points
        user_points.level = user_points.calculate_level()

        today = timezone.now().date()
        if user_points.last_activity_date == today - timedelta(days=1):
            user_points.streak_days += 1
        elif user_points.last_activity_date != today:
            user_points.streak_days = 1
        user_points.last_activity_date = today
        user_points.save()

        GamificationEngine._check_badges(user)
        return transaction

    @staticmethod
    def _check_badges(user):
        user_points = UserPoints.objects.filter(user=user).first()
        if not user_points:
            return

        earned_badges = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        available_badges = Badge.objects.filter(is_active=True).exclude(id__in=earned_badges)

        for badge in available_badges:
            if user_points.total_points >= badge.points_required:
                UserBadge.objects.create(
                    user=user, badge=badge,
                    reason=f"Achieved {badge.tier} tier with {user_points.total_points} points"
                )

    @staticmethod
    def get_leaderboard(period='MONTHLY', school=None, limit=20):
        now = timezone.now()
        if period == 'WEEKLY':
            start = now - timedelta(days=7)
        elif period == 'MONTHLY':
            start = now - timedelta(days=30)
        elif period == 'TERM':
            start = now - timedelta(days=120)
        else:
            start = timezone.datetime(2020, 1, 1, tzinfo=timezone.utc)

        users = UserPoints.objects.all()
        if school:
            users = users.filter(user__school=school)

        leaderboard = []
        for i, up in enumerate(users.order_by('-total_points')[:limit], 1):
            leaderboard.append({
                'rank': i,
                'user_id': up.user_id,
                'name': up.user.get_full_name(),
                'level': up.level,
                'total_points': up.total_points,
                'streak_days': up.streak_days,
            })
        return leaderboard

    @staticmethod
    def get_user_stats(user):
        user_points = UserPoints.objects.filter(user=user).first()
        if not user_points:
            user_points = UserPoints.objects.create(user=user)

        transactions = PointTransaction.objects.filter(user=user)
        badges = UserBadge.objects.filter(user=user).select_related('badge')

        recent_transactions = transactions[:10]
        category_breakdown = transactions.values('category__name').annotate(
            total=Sum('points')
        ).order_by('-total')

        return {
            'total_points': user_points.total_points,
            'level': user_points.level,
            'streak_days': user_points.streak_days,
            'badges_count': badges.count(),
            'badges': [{'name': b.badge.name, 'icon': b.badge.icon, 'tier': b.badge.tier}
                       for b in badges],
            'recent_transactions': [{
                'category': t.category.name,
                'points': t.points,
                'description': t.description,
                'date': t.created_at.strftime('%d %b %Y'),
            } for t in recent_transactions],
            'category_breakdown': list(category_breakdown),
        }

    @staticmethod
    def initialize_default_categories():
        categories = [
            ('ATTENDANCE', 'Perfect Attendance', 15, 'Present every day for a week'),
            ('ACADEMIC', 'Academic Excellence', 25, 'Score 80%+ in exams'),
            ('ASSIGNMENT', 'Assignment Submission', 10, 'Submit assignments on time'),
            ('PARTICIPATION', 'Class Participation', 10, 'Active class participation'),
            ('LEADERSHIP', 'Leadership Role', 20, 'Held leadership position'),
            ('COMMUNITY', 'Community Service', 30, 'Volunteer activities'),
            ('PROFESSIONAL', 'Professional Development', 20, 'Complete training'),
            ('ADMINISTRATIVE', 'Administrative Efficiency', 15, 'Complete tasks early'),
            ('INNOVATION', 'Innovation', 25, 'Propose/implement new ideas'),
            ('MENTORING', 'Mentoring', 20, 'Mentor students/junior staff'),
        ]
        for action, name, points, desc in categories:
            PointCategory.objects.update_or_create(
                action_type=action,
                defaults={'name': name, 'points': points, 'description': desc}
            )

    @staticmethod
    def initialize_default_badges():
        badges = [
            ('First Steps', 'Complete your first action', '👟', 'BRONZE', 50),
            ('Rising Star', 'Earn 100 points', '⭐', 'BRONZE', 100),
            ('Achiever', 'Earn 500 points', '🏅', 'SILVER', 500),
            ('Champion', 'Earn 1000 points', '🏆', 'GOLD', 1000),
            ('Legend', 'Earn 5000 points', '👑', 'PLATINUM', 5000),
            ('Mythic', 'Earn 10000 points', '💎', 'DIAMOND', 10000),
            ('Perfect Week', '7-day attendance streak', '📅', 'BRONZE', 0),
            ('Perfect Month', '30-day attendance streak', '🗓️', 'SILVER', 0),
            ('Bookworm', 'Submit 10 assignments', '📚', 'BRONZE', 0),
            ('Innovator', 'Propose an innovation', '💡', 'SILVER', 0),
            ('Mentor', 'Complete mentoring program', '🎓', 'GOLD', 0),
            ('Community Hero', '100 community service hours', '🦸', 'PLATINUM', 0),
        ]
        for name, desc, icon, tier, points in badges:
            Badge.objects.update_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon, 'tier': tier, 'points_required': points}
            )
