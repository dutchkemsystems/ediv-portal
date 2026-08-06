from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PointCategoryViewSet, BadgeViewSet, UserPointsViewSet,
    PointTransactionViewSet, UserBadgeViewSet, LeaderboardViewSet
)

router = DefaultRouter()
router.register('categories', PointCategoryViewSet, basename='point-category')
router.register('badges', BadgeViewSet, basename='badge')
router.register('points', UserPointsViewSet, basename='user-points')
router.register('transactions', PointTransactionViewSet, basename='point-transaction')
router.register('user-badges', UserBadgeViewSet, basename='user-badge')
router.register('leaderboards', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('', include(router.urls)),
]
