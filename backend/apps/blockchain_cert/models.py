from django.db import models
from django.conf import settings


class Certificate(models.Model):
    CERT_TYPE_CHOICES = [
        ('TRANScript', 'Transcript'),
        ('LEAVING', 'Leaving Certificate'),
        ('MERIT', 'Merit Certificate'),
        ('PARTICIPATION', 'Participation Certificate'),
        ('ATHLETIC', 'Athletic Certificate'),
        ('ACADEMIC', 'Academic Excellence'),
        ('CUSTOM', 'Custom Certificate'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='blockchain_certificates')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='blockchain_certificates')
    certificate_type = models.CharField(max_length=20, choices=CERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issued_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)

    # Blockchain fields
    cert_hash = models.CharField(max_length=64, unique=True, db_index=True)
    previous_hash = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(default=0)
    block_data = models.JSONField(default=dict)

    # Issuer
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    principal_signature = models.CharField(max_length=500, blank=True)

    # Status
    is_revoked = models.BooleanField(default=False)
    revocation_reason = models.TextField(blank=True)
    verified_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blockchain_certificates'
        ordering = ['-issued_date']

    def __str__(self):
        return f"{self.title} - {self.student}"


class CertificateVerification(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verifications')
    verified_by = models.CharField(max_length=200)
    verification_method = models.CharField(max_length=50, choices=[
        ('QR_CODE', 'QR Code Scan'),
        ('HASH', 'Hash Lookup'),
        ('URL', 'Direct URL'),
        ('API', 'API Verification'),
    ])
    ip_address = models.GenericIPAddressField(null=True)
    is_valid = models.BooleanField()
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certificate_verifications'
        ordering = ['-verified_at']

    def __str__(self):
        return f"Verification: {self.certificate.cert_hash[:16]}... by {self.verified_by}"
