from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet, PrivilegeViewSet, RolePrivilegeViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('auth', AuthViewSet, basename='auth')
router.register('privileges', PrivilegeViewSet)
router.register('role-privileges', RolePrivilegeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
