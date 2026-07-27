from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet, PrivilegeViewSet, RolePrivilegeViewSet, UnlockView

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('auth', AuthViewSet, basename='auth')
router.register('privileges', PrivilegeViewSet)
router.register('role-privileges', RolePrivilegeViewSet)

# Unlock endpoint must be CSRF-exempt and bypass DRF's normal auth flow.
# We use a separate dedicated view (not the ViewSet) so we can apply
# csrf_exempt at the URL level without affecting other auth endpoints.
urlpatterns = [
    path('auth/unlock/', csrf_exempt(UnlockView.as_view()), name='auth-unlock'),
    path('', include(router.urls)),
]
