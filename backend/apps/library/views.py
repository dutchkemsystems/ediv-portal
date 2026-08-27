from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from config.permissions import IsSchoolStaffOrAdmin

from .models import Book, BookLoan
from .serializers import BookListSerializer, BookLoanSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("school").all()
    permission_classes = [IsSchoolStaffOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["school", "category", "is_active"]
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer


class BookLoanViewSet(viewsets.ModelViewSet):
    queryset = BookLoan.objects.select_related("book", "borrower", "issued_by").all()
    serializer_class = BookLoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["book", "borrower", "status"]
    search_fields = ["book__title", "borrower__first_name", "borrower__last_name"]
    ordering_fields = ["loan_date", "due_date", "created_at"]
