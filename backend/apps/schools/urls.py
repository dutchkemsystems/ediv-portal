from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SchoolAcademicYearViewSet

router = DefaultRouter()
router.register('schools', SchoolViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('schools/<int:school_pk>/academic-years/', SchoolAcademicYearViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('schools/<int:school_pk>/academic-years/<int:pk>/', SchoolAcademicYearViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]
