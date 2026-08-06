from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Certificate, CertificateVerification
from .serializers import (
    CertificateSerializer, CertificateVerificationSerializer,
    VerifyCertificateRequestSerializer
)
from .services.blockchain import CertificateBlockchain


class IsIssuerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('SYSADMIN', 'TG_PS', 'PRINCIPAL', 'VP')


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsIssuerOrReadOnly]
    filterset_fields = ['certificate_type', 'school', 'is_revoked']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'title']
    ordering_fields = ['-issued_date']

    def perform_create(self, serializer):
        instance = serializer.save(issued_by=self.request.user)
        block_data = CertificateBlockchain.generate_certificate_data(
            instance.student, instance.school,
            instance.certificate_type, instance.title,
            instance.issued_date
        )
        previous_hash = Certificate.objects.exclude(id=instance.id).order_by('-id').first()
        prev_hash = previous_hash.cert_hash if previous_hash else '0' * 64

        block = CertificateBlockchain.mine_block(block_data, prev_hash)
        instance.cert_hash = block['hash']
        instance.previous_hash = block['previous_hash']
        instance.nonce = block['nonce']
        instance.block_data = block['data']
        instance.save()

    @action(detail=True, methods=['get'], url_path='verify-hash')
    def verify_hash(self, request, pk=None):
        cert = self.get_object()
        is_valid = CertificateBlockchain.verify_certificate(
            cert.block_data, cert.cert_hash, cert.previous_hash, cert.nonce
        )
        CertificateVerification.objects.create(
            certificate=cert,
            verified_by=request.user.get_full_name(),
            verification_method='HASH',
            ip_address=request.META.get('REMOTE_ADDR'),
            is_valid=is_valid,
        )
        if is_valid:
            cert.verified_count += 1
            cert.save(update_fields=['verified_count'])
        return Response({
            'valid': is_valid,
            'cert_hash': cert.cert_hash,
            'certificate': CertificateSerializer(cert).data,
        })

    @action(detail=False, methods=['post'], url_path='public-verify')
    def public_verify(self, request):
        serializer = VerifyCertificateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cert_hash = serializer.validated_data['cert_hash']

        cert = Certificate.objects.filter(cert_hash=cert_hash).first()
        if not cert:
            return Response({'valid': False, 'error': 'Certificate not found'},
                          status=status.HTTP_404_NOT_FOUND)

        is_valid = CertificateBlockchain.verify_certificate(
            cert.block_data, cert.cert_hash, cert.previous_hash, cert.nonce
        )
        CertificateVerification.objects.create(
            certificate=cert,
            verified_by=serializer.validated_data.get('verified_by', 'Public User'),
            verification_method='URL',
            ip_address=request.META.get('REMOTE_ADDR'),
            is_valid=is_valid,
        )
        if is_valid:
            cert.verified_count += 1
            cert.save(update_fields=['verified_count'])

        return Response({
            'valid': is_valid and not cert.is_revoked,
            'certificate': CertificateSerializer(cert).data,
            'message': 'Certificate verified successfully.' if is_valid and not cert.is_revoked
                      else 'Certificate is invalid or has been revoked.',
        })

    @action(detail=True, methods=['post'], url_path='revoke')
    def revoke_certificate(self, request, pk=None):
        cert = self.get_object()
        if request.user.role not in ('SYSADMIN', 'TG_PS'):
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        cert.is_revoked = True
        cert.revocation_reason = request.data.get('reason', '')
        cert.save()
        return Response({'message': 'Certificate revoked.'})

    @action(detail=True, methods=['get'], url_path='revoke-history')
    def revoke_history(self, request, pk=None):
        cert = self.get_object()
        return Response({
            'is_revoked': cert.is_revoked,
            'revocation_reason': cert.revocation_reason,
            'verified_count': cert.verified_count,
        })

    @action(detail=False, methods=['get'], url_path='my-certificates')
    def my_certificates(self, request):
        from apps.students.models import Student
        student = Student.objects.filter(user=request.user).first()
        if not student:
            return Response([])
        certs = Certificate.objects.filter(student=student, is_revoked=False)
        return Response(CertificateSerializer(certs, many=True).data)

    @action(detail=True, methods=['get'], url_path='qr-data')
    def qr_data(self, request, pk=None):
        cert = self.get_object()
        qr_url = CertificateBlockchain.generate_qr_data(cert.cert_hash)
        return Response({'qr_url': qr_url, 'cert_hash': cert.cert_hash})
