from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PointCategory, Badge, UserPoints, PointTransaction, UserBadge, Leaderboard
from .serializers import (
    PointCategorySerializer, BadgeSerializer, UserPointsSerializer,
    PointTransactionSerializer, UserBadgeSerializer, LeaderboardSerializer
)
from .services.gamification_engine import GamificationEngine


class PointCategoryViewSet(viewsets.ModelViewSet):
    queryset = PointCategory.objects.all()
    serializer_class = PointCategorySerializer
    permission_classes = [permissions.IsAdminUser]


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAdminUser]


class UserPointsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPointsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPoints.objects.all()

    @action(detail=False, methods=['get'], url_path='my-stats')
    def my_stats(self, request):
        stats = GamificationEngine.get_user_stats(request.user)
        return Response(stats)

    @action(detail=False, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request):
        period = request.query_params.get('period', 'MONTHLY')
        leaderboard = GamificationEngine.get_leaderboard(period=period)
        return Response(leaderboard)

    @action(detail=False, methods=['post'], url_path='award')
    def award_points(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        action_type = request.data.get('action_type')
        description = request.data.get('description', '')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        transaction = GamificationEngine.award_points(
            target_user, action_type, description, awarded_by=request.user
        )
        if transaction:
            return Response({'message': f'Awarded {transaction.points} points'})
        return Response({'error': 'Could not award points'}, status=status.HTTP_400_BAD_REQUEST)


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PointTransaction.objects.all()
        return PointTransaction.objects.filter(user=self.request.user)


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserBadge.objects.all()
        return UserBadge.objects.filter(user=self.request.user)


class LeaderboardViewSet(viewsets.ModelViewSet):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
