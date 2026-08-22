from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookLoanViewSet, BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet)
router.register("loans", BookLoanViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
