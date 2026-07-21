from rest_framework import serializers
from .models import Book, BookLoan


class BookSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = ['id', 'school', 'school_name', 'title', 'author', 'isbn', 'category',
                  'publisher', 'publication_year', 'edition', 'description', 'total_copies',
                  'available_copies', 'location', 'cover_image', 'is_active', 'is_available',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


class BookListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = ['id', 'school_name', 'title', 'author', 'isbn', 'category', 'is_available']
    
    def get_school_name(self, obj):
        return obj.school.name


class BookLoanSerializer(serializers.ModelSerializer):
    book_title = serializers.SerializerMethodField()
    borrower_name = serializers.SerializerMethodField()
    issued_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BookLoan
        fields = ['id', 'book', 'book_title', 'borrower', 'borrower_name', 'loan_date',
                  'due_date', 'return_date', 'status', 'issued_by', 'issued_by_name',
                  'notes', 'fine_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_book_title(self, obj):
        return obj.book.title
    
    def get_borrower_name(self, obj):
        return obj.borrower.get_full_name()
    
    def get_issued_by_name(self, obj):
        if obj.issued_by:
            return obj.issued_by.get_full_name()
        return None

