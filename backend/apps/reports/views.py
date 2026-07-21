from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from .models import Report, Dashboard, Widget
from .serializers import (
    ReportSerializer, DashboardSerializer,
    DashboardListSerializer, WidgetSerializer
)
from .exporters import ExcelExporter, PDFExporter, WordExporter, CSVExporter, JPEGExporter
from .importers import ExcelImporter, CSVImporter, PDFImporter, WordImporter, DataValidator


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related('generated_by').all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['report_type', 'is_scheduled']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'last_generated']
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def export(self, request, pk=None):
        report = self.get_object()
        export_format = request.data.get('format', 'excel')
        
        # Get report data based on type
        data = self._get_report_data(report)
        
        if export_format == 'excel':
            wb = ExcelExporter.export_to_excel(data, report.title)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{report.title}.xlsx"'
            wb.save(response)
            return response
        
        elif export_format == 'pdf':
            buffer = PDFExporter.export_to_pdf(data, report.title, report.title)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
            return response
        
        elif export_format == 'word':
            buffer = WordExporter.export_to_word(data, report.title, report.title)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{report.title}.docx"'
            return response
        
        elif export_format == 'jpeg':
            buffer = JPEGExporter.export_to_jpeg(data, report.title, report.title)
            response = HttpResponse(buffer.getvalue(), content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename="{report.title}.jpg"'
            return response
        
        return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def import_data(self, request):
        file = request.FILES.get('file')
        import_type = request.data.get('type', 'students')
        
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        filename = file.name.lower()
        
        try:
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                result = ExcelImporter.import_from_excel(file)
            elif filename.endswith('.csv'):
                result = CSVImporter.import_from_csv(file)
            elif filename.endswith('.pdf'):
                result = PDFImporter.extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                result = WordImporter.extract_from_word(file)
            else:
                return Response(
                    {'error': 'Unsupported file format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate based on type
            if import_type == 'students':
                validation = DataValidator.validate_student_data(result.get('data', []))
            elif import_type == 'staff':
                validation = DataValidator.validate_staff_data(result.get('data', []))
            else:
                validation = {'valid': True, 'data': result.get('data', [])}
            
            return Response({
                'success': True,
                'data': result,
                'validation': validation
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_report_data(self, report):
        # This would be implemented based on report type
        # For now, return empty list
        return []


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.select_related('owner').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DashboardListSerializer
        return DashboardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(
            models.Q(owner=user) | models.Q(is_default=True)
        ).distinct()


class WidgetViewSet(viewsets.ModelViewSet):
    queryset = Widget.objects.select_related('dashboard').all()
    serializer_class = WidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['dashboard', 'widget_type', 'is_active']
