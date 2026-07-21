from django.contrib import admin
from .models import Book, BookLoan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'school', 'category', 'total_copies', 'available_copies']
    list_filter = ['school', 'category', 'is_active']
    search_fields = ['title', 'author', 'isbn']
    raw_id_fields = ['school']


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower', 'loan_date', 'due_date', 'return_date', 'status']
    list_filter = ['status']
    search_fields = ['book__title', 'borrower__first_name', 'borrower__last_name']
    raw_id_fields = ['book', 'borrower', 'issued_by']
