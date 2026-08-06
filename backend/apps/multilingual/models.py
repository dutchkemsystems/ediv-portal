from django.db import models
from django.conf import settings


class UserLanguagePreference(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('yo', 'Yoruba'),
        ('pcm', 'Nigerian Pidgin'),
        ('fr', 'French'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='language_preference')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    auto_detect = models.BooleanField(default=True)
    font_size = models.CharField(max_length=10, default='medium',
                                 choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_language_preferences'

    def __str__(self):
        return f"{self.user.email} - {self.preferred_language}"


class TranslationEntry(models.Model):
    key = models.CharField(max_length=200, db_index=True)
    language = models.CharField(max_length=5)
    value = models.TextField()
    context = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'translation_entries'
        unique_together = ['key', 'language', 'context']

    def __str__(self):
        return f"{self.key} ({self.language}): {self.value[:50]}"
