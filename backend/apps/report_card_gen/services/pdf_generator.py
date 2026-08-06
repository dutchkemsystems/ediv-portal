import os
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from ..models import GeneratedReportCard, ReportCardTemplate


class ReportCardGenerator:
    @staticmethod
    def generate_report_card(student, academic_session, term, generated_by=None):
        template = ReportCardTemplate.objects.filter(is_active=True).first()
        if not template:
            template = ReportCardTemplate.objects.create(
                name='Default Template',
                header_text='Education District IV - Lagos State',
                footer_text='Excellence in Education'
            )

        report_card, created = GeneratedReportCard.objects.get_or_create(
            student=student,
            academic_session=academic_session,
            term=term,
            defaults={
                'school': student.school,
                'template': template,
                'generated_by': generated_by,
                'status': 'GENERATING',
            }
        )

        if not created and report_card.status == 'COMPLETED':
            return report_card

        try:
            from django.db.models import Avg
            from apps.students.models import AcademicRecord
            records = AcademicRecord.objects.filter(
                student=student,
                academic_session=academic_session,
                term=term
            )

            total = sum(r.score for r in records)
            count = records.count()
            average = total / count if count > 0 else 0

            all_students_avg = AcademicRecord.objects.filter(
                academic_session=academic_session,
                term=term
            ).values('student').annotate(
                avg=Avg('score')
            ).order_by('-avg')

            position = 1
            for i, s in enumerate(all_students_avg, 1):
                if s['student'] == student.id:
                    position = i
                    break

            report_card.total_score = total
            report_card.average_score = round(average, 2)
            report_card.position = position
            report_card.total_students = all_students_avg.count()
            report_card.remark = ReportCardGenerator._get_remark(average)
            report_card.status = 'COMPLETED'
            report_card.generated_at = timezone.now()
            report_card.save()

            ReportCardGenerator._generate_pdf(report_card, records)

            return report_card

        except Exception as e:
            report_card.status = 'FAILED'
            report_card.error_message = str(e)
            report_card.save()
            raise

    @staticmethod
    def _get_remark(average):
        if average >= 80:
            return "Excellent performance. Keep it up!"
        elif average >= 70:
            return "Very good performance. Maintain the standard."
        elif average >= 60:
            return "Good performance. There is room for improvement."
        elif average >= 50:
            return "Fair performance. More effort needed."
        else:
            return "Needs significant improvement. Please see guidance counselor."

    @staticmethod
    def _generate_pdf(report_card, records):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=20*mm, bottomMargin=20*mm,
                               leftMargin=15*mm, rightMargin=15*mm)

        styles = getSampleStyleSheet()
        elements = []

        header_style = ParagraphStyle('Header', parent=styles['Heading1'],
                                      alignment=TA_CENTER, fontSize=16,
                                      spaceAfter=5)
        subheader_style = ParagraphStyle('SubHeader', parent=styles['Heading2'],
                                         alignment=TA_CENTER, fontSize=12,
                                         spaceAfter=10)

        elements.append(Paragraph(report_card.school.name, header_style))
        elements.append(Paragraph(report_card.template.header_text, subheader_style))
        elements.append(Spacer(1, 10))

        student_info = [
            ['Student Name:', report_card.student.user.get_full_name()],
            ['Student ID:', report_card.student.student_id],
            ['Class:', str(report_card.student.class_level)],
            ['Session:', report_card.academic_session],
            ['Term:', report_card.term],
        ]
        student_table = Table(student_info, colWidths=[100, 300])
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph('<b>Academic Results</b>', styles['Heading3']))
        table_data = [['Subject', 'Score', 'Grade', 'Remark']]
        for record in records:
            table_data.append([
                record.subject,
                f'{record.score}%',
                record.grade,
                record.remark or ''
            ])

        table_data.append([
            'Total', f'{report_card.total_score}', '', ''
        ])
        table_data.append([
            'Average', f'{report_card.average_score}%', '', report_card.remark
        ])

        result_table = Table(table_data, colWidths=[150, 80, 60, 160])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#E3F2FD')),
        ]))
        elements.append(result_table)
        elements.append(Spacer(1, 20))

        if report_card.position:
            elements.append(Paragraph(
                f'<b>Class Position:</b> {report_card.position} out of {report_card.total_students}',
                styles['Normal']
            ))
            elements.append(Spacer(1, 10))

        if report_card.teacher_remark:
            elements.append(Paragraph(f'<b>Class Teacher Remark:</b>', styles['Normal']))
            elements.append(Paragraph(report_card.teacher_remark, styles['Normal']))
            elements.append(Spacer(1, 10))

        if report_card.principal_remark:
            elements.append(Paragraph(f'<b>Principal Remark:</b>', styles['Normal']))
            elements.append(Paragraph(report_card.principal_remark, styles['Normal']))
            elements.append(Spacer(1, 20))

        elements.append(Paragraph(report_card.template.footer_text, subheader_style))

        doc.build(elements)

        pdf_content = buffer.getvalue()
        buffer.close()

        filename = f"report_card_{report_card.student.student_id}_{report_card.term}_{report_card.academic_session}.pdf"
        report_card.pdf_file.save(filename, pdf_content, save=True)

    @staticmethod
    def generate_batch(school_id, academic_session, term, class_level=None):
        from apps.students.models import Student
        students = Student.objects.filter(school_id=school_id)
        if class_level:
            students = students.filter(class_level=class_level)

        results = []
        for student in students:
            try:
                report = ReportCardGenerator.generate_report_card(
                    student, academic_session, term
                )
                results.append({
                    'student': student.user.get_full_name(),
                    'status': report.status,
                })
            except Exception as e:
                results.append({
                    'student': student.user.get_full_name(),
                    'status': 'FAILED',
                    'error': str(e),
                })

        return results
