from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookLoanViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('loans', BookLoanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
