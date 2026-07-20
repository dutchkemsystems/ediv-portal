from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, UnitViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet)
router.register('units', UnitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
