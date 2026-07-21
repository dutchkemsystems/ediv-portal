from django.db import models
from django.conf import settings
from apps.schools.models import School


class BookCategory(models.TextChoices):
    FICTION = 'FICTION', 'Fiction'
    NON_FICTION = 'NON_FICTION', 'Non-Fiction'
    TEXTBOOK = 'TEXTBOOK', 'Textbook'
    REFERENCE = 'REFERENCE', 'Reference'
    ACADEMIC = 'ACADEMIC', 'Academic'
    CHILDREN = 'CHILDREN', 'Children'
    SCIENCE = 'SCIENCE', 'Science'
    TECHNOLOGY = 'TECHNOLOGY', 'Technology'
    HISTORY = 'HISTORY', 'History'
    LITERATURE = 'LITERATURE', 'Literature'
    OTHER = 'OTHER', 'Other'


class Book(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=BookCategory.choices)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    location = models.CharField(max_length=100, blank=True)
    cover_image = models.FileField(upload_to='books/covers/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['isbn']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0


class BookLoan(models.Model):
    class LoanStatus(models.TextChoices):
        BORROWED = 'BORROWED', 'Borrowed'
        RETURNED = 'RETURNED', 'Returned'
        OVERDUE = 'OVERDUE', 'Overdue'
        LOST = 'LOST', 'Lost'
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_loans'
    )
    loan_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default='BORROWED')
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_books'
    )
    notes = models.TextField(blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-loan_date']
        indexes = [
            models.Index(fields=['book']),
            models.Index(fields=['borrower']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.book.title} - {self.borrower.get_full_name()}"
