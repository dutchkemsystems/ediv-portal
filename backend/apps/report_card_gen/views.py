from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ReportCardTemplate, GeneratedReportCard, ReportCardShareLog
from .serializers import (
    ReportCardTemplateSerializer, GeneratedReportCardSerializer,
    ReportCardShareLogSerializer, GenerateReportCardSerializer,
    ShareReportCardSerializer
)
from .services.pdf_generator import ReportCardGenerator


class ReportCardTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportCardTemplate.objects.all()
    serializer_class = ReportCardTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class GeneratedReportCardViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedReportCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return GeneratedReportCard.objects.all()
        return GeneratedReportCard.objects.filter(
            student__user=self.request.user
        )

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_cards(self, request):
        serializer = GenerateReportCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.students.models import Student
        student_ids = serializer.validated_data['student_ids']
        academic_session = serializer.validated_data['academic_session']
        term = serializer.validated_data['term']

        results = []
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                report = ReportCardGenerator.generate_report_card(
                    student, academic_session, term, generated_by=request.user
                )
                results.append({
                    'student_id': student_id,
                    'student_name': student.user.get_full_name(),
                    'status': report.status,
                    'report_id': report.id,
                })
            except Student.DoesNotExist:
                results.append({
                    'student_id': student_id,
                    'status': 'FAILED',
                    'error': 'Student not found',
                })
            except Exception as e:
                results.append({
                    'student_id': student_id,
                    'status': 'FAILED',
                    'error': str(e),
                })

        return Response({
            'message': f'Processed {len(results)} report cards',
            'results': results,
        })

    @action(detail=False, methods=['post'], url_path='generate-batch')
    def generate_batch(self, request):
        school_id = request.data.get('school_id')
        academic_session = request.data.get('academic_session')
        term = request.data.get('term')
        class_level = request.data.get('class_level')

        if not school_id or not academic_session or not term:
            return Response({'error': 'school_id, academic_session, and term required'},
                          status=status.HTTP_400_BAD_REQUEST)

        results = ReportCardGenerator.generate_batch(
            school_id, academic_session, term, class_level
        )
        return Response({
            'message': f'Generated {len(results)} report cards',
            'results': results,
        })

    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        report = self.get_object()
        if not report.pdf_file:
            return Response({'error': 'PDF not generated yet'},
                          status=status.HTTP_404_NOT_FOUND)
        return Response({'pdf_url': report.pdf_file.url})

    @action(detail=True, methods=['post'], url_path='share')
    def share_report(self, request, pk=None):
        report = self.get_object()
        channel = request.data.get('channel', 'DOWNLOAD')
        recipient = request.data.get('recipient', '')

        share_log = ReportCardShareLog.objects.create(
            report_card=report,
            channel=channel,
            recipient=recipient,
            shared_by=request.user,
        )

        if channel == 'WHATSAPP' and report.pdf_file:
            share_url = report.pdf_file.url
            return Response({
                'message': 'Share link generated',
                'share_url': share_url,
                'whatsapp_text': f"Report Card for {report.student.user.get_full_name()} is ready. Download: {share_url}",
            })

        return Response({'message': f'Report card shared via {channel}'})


class ReportCardShareLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportCardShareLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ReportCardShareLog.objects.all()
        return ReportCardShareLog.objects.filter(
            report_card__student__user=self.request.user
        )
