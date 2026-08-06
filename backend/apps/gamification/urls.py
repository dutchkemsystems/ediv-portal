from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PointCategoryViewSet, BadgeViewSet, UserPointsViewSet,
    PointTransactionViewSet, UserBadgeViewSet, LeaderboardViewSet
)

router = DefaultRouter()
router.register('categories', PointCategoryViewSet)
router.register('badges', BadgeViewSet)
router.register('points', UserPointsViewSet)
router.register('transactions', PointTransactionViewSet)
router.register('user-badges', UserBadgeViewSet)
router.register('leaderboards', LeaderboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
