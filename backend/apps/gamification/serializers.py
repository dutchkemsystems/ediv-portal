from rest_framework import serializers
from .models import PointCategory, Badge, UserPoints, PointTransaction, UserBadge, Leaderboard


class PointCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PointCategory
        fields = ['id', 'name', 'action_type', 'points', 'description', 'is_active', 'daily_limit']


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon', 'tier', 'points_required', 'category', 'criteria']


class UserPointsSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserPoints
        fields = ['id', 'user', 'user_name', 'total_points', 'level', 'streak_days', 'last_activity_date']
        read_only_fields = ['id', 'total_points', 'level']

    def get_user_name(self, obj):
        return obj.user.get_full_name()


class PointTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = PointTransaction
        fields = ['id', 'user', 'user_name', 'category', 'category_name', 'points',
                  'description', 'reference_id', 'awarded_by', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_category_name(self, obj):
        return obj.category.name


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.SerializerMethodField()
    badge_icon = serializers.SerializerMethodField()
    badge_tier = serializers.SerializerMethodField()

    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'badge', 'badge_name', 'badge_icon', 'badge_tier',
                  'awarded_at', 'awarded_by', 'reason']

    def get_badge_name(self, obj):
        return obj.badge.name

    def get_badge_icon(self, obj):
        return obj.badge.icon

    def get_badge_tier(self, obj):
        return obj.badge.tier


class LeaderboardSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Leaderboard
        fields = ['id', 'user', 'user_name', 'period', 'period_start', 'period_end',
                  'points_earned', 'rank', 'school']

    def get_user_name(self, obj):
        return obj.user.get_full_name()
