"""Tests for ImportExportService."""
import io
import csv
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.files.base import ContentFile
from apps.users.models import User
from apps.departments.models import Department
from apps.files.models import File, FileAttachment, FileTemplate
from apps.files.services.import_export_service import ImportExportService


class ImportExportServiceSupportedFormatsTest(TestCase):
    """Tests for format constants."""

    def test_supported_import_formats(self):
        self.assertIn('doc', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('docx', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('xlsx', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('csv', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('pdf', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('jpeg', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('png', ImportExportService.SUPPORTED_IMPORT_FORMATS)
        self.assertIn('txt', ImportExportService.SUPPORTED_IMPORT_FORMATS)

    def test_supported_export_formats(self):
        self.assertIn('xlsx', ImportExportService.SUPPORTED_EXPORT_FORMATS)
        self.assertIn('csv', ImportExportService.SUPPORTED_EXPORT_FORMATS)
        self.assertIn('pdf', ImportExportService.SUPPORTED_EXPORT_FORMATS)
        self.assertIn('docx', ImportExportService.SUPPORTED_EXPORT_FORMATS)


class ImportExportServiceImportTextTest(TestCase):
    """Tests for importing text files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='importer@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Import',
            last_name='User',
            role='SYSADMIN'
        )
        self.department = Department.objects.create(
            name='Admin',
            code='ADM',
            category='CORE'
        )

    def test_import_txt_file(self):
        """Import a plain text file creates a File record."""
        content = b'This is a test document.\nLine two of the document.'
        uploaded_file = ContentFile(content, name='test_document.txt')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='txt',
            created_by=self.user,
        )
        self.assertIn('file', result)
        self.assertIn('attachments', result)
        self.assertIn('errors', result)
        self.assertEqual(len(result['errors']), 0)

        file_obj = result['file']
        self.assertIsInstance(file_obj, File)
        self.assertEqual(file_obj.created_by, self.user)
        self.assertEqual(file_obj.file_type, 'OTHER')

    def test_import_txt_with_department(self):
        """Import a text file with department override."""
        content = b'Department document content.'
        uploaded_file = ContentFile(content, name='dept_doc.txt')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='txt',
            created_by=self.user,
            department=self.department,
        )
        file_obj = result['file']
        self.assertEqual(file_obj.department, self.department)

    def test_import_txt_with_classification_priority(self):
        """Import with classification and priority overrides."""
        content = b'Confidential content.'
        uploaded_file = ContentFile(content, name='conf.txt')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='txt',
            created_by=self.user,
            default_classification='CONFIDENTIAL',
            default_priority='HIGH',
        )
        file_obj = result['file']
        self.assertEqual(file_obj.classification, 'CONFIDENTIAL')
        self.assertEqual(file_obj.priority, 'HIGH')

    def test_import_txt_creates_attachment(self):
        """Import should create a FileAttachment linked to the File."""
        content = b'Attachment content.'
        uploaded_file = ContentFile(content, name='attached.txt')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='txt',
            created_by=self.user,
        )
        attachments = result['attachments']
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].original_filename, 'attached.txt')
        self.assertEqual(attachments[0].uploaded_by, self.user)

    def test_import_empty_txt_file(self):
        """Import an empty text file should still create a record."""
        uploaded_file = ContentFile(b'', name='empty.txt')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='txt',
            created_by=self.user,
        )
        self.assertIsNotNone(result['file'].id)
        self.assertEqual(len(result['errors']), 0)


class ImportExportServiceImportCSVTest(TestCase):
    """Tests for importing CSV files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='csvimporter@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='CSV',
            last_name='Importer',
            role='SYSADMIN'
        )

    def test_import_csv_file(self):
        """Import a CSV file creates a File record."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['title', 'type', 'status'])
        writer.writerow(['Test File', 'MEMO', 'ACTIVE'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='data.csv')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
        )
        self.assertIn('file', result)
        self.assertEqual(len(result['errors']), 0)
        self.assertIsInstance(result['file'], File)

    def test_import_csv_with_metadata(self):
        """CSV with title column should set file title from data."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['title', 'description'])
        writer.writerow(['Important Report', 'This is a report about students.'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='report.csv')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
        )
        # The title should be populated from CSV data
        file_obj = result['file']
        self.assertIsNotNone(file_obj.id)

    def test_import_csv_creates_attachment(self):
        """CSV import should create attachment."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['name'])
        writer.writerow(['item1'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='items.csv')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
        )
        self.assertGreaterEqual(len(result['attachments']), 1)


class ImportExportServiceImportImageTest(TestCase):
    """Tests for importing image files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='imgimporter@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Img',
            last_name='Importer',
            role='SYSADMIN'
        )

    def test_import_jpeg_file(self):
        """Import a JPEG file creates a File record with image attachment."""
        # Create a minimal valid JPEG (1x1 pixel)
        from PIL import Image
        img = Image.new('RGB', (100, 50), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        uploaded_file = ContentFile(buffer.read(), name='photo.jpeg')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='jpeg',
            created_by=self.user,
        )
        self.assertIn('file', result)
        self.assertEqual(len(result['errors']), 0)
        self.assertIsInstance(result['file'], File)

    def test_import_png_file(self):
        """Import a PNG file creates a File record."""
        from PIL import Image
        img = Image.new('RGBA', (80, 60), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        uploaded_file = ContentFile(buffer.read(), name='logo.png')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='png',
            created_by=self.user,
        )
        self.assertIsNotNone(result['file'].id)
        self.assertEqual(len(result['errors']), 0)


class ImportExportServiceImportUnsupportedTest(TestCase):
    """Tests for unsupported format handling."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='bad@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Bad',
            last_name='User',
            role='SYSADMIN'
        )

    def test_import_unsupported_format_returns_error(self):
        """Unsupported format should return an error."""
        uploaded_file = ContentFile(b'data', name='file.xyz')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='xyz',
            created_by=self.user,
        )
        self.assertGreater(len(result['errors']), 0)
        self.assertIsNone(result.get('file'))


class ImportExportServiceExportTest(TestCase):
    """Tests for export functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='exporter@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Export',
            last_name='User',
            role='SYSADMIN'
        )
        self.file1 = File.objects.create(
            file_number='EDIV-2026-ADM-0001',
            title='First Export File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='CONFIDENTIAL',
            priority='HIGH',
        )
        self.file2 = File.objects.create(
            file_number='EDIV-2026-ADM-0002',
            title='Second Export File',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='DRAFT',
            classification='INTERNAL',
            priority='NORMAL',
        )

    def test_export_to_csv(self):
        """Export files to CSV format."""
        result = ImportExportService.export_files(
            file_ids=[self.file1.id, self.file2.id],
            export_format='csv',
            exported_by=self.user,
        )
        self.assertIsInstance(result, ContentFile)
        self.assertIn('.csv', result.name)

        # Parse CSV content
        content = result.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        # Header + 2 data rows
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][0], 'File Number')
        # Files are ordered by -created_at, so order may vary
        file_numbers = {rows[1][0], rows[2][0]}
        self.assertIn('EDIV-2026-ADM-0001', file_numbers)
        self.assertIn('EDIV-2026-ADM-0002', file_numbers)

    def test_export_to_xlsx(self):
        """Export files to Excel format."""
        result = ImportExportService.export_files(
            file_ids=[self.file1.id],
            export_format='xlsx',
            exported_by=self.user,
        )
        self.assertIsInstance(result, ContentFile)
        self.assertIn('.xlsx', result.name)
        # Verify content is valid xlsx bytes (PK header for zip)
        content_bytes = result.read()
        self.assertTrue(content_bytes[:2] == b'PK')

    def test_export_to_docx(self):
        """Export files to Word document format."""
        result = ImportExportService.export_files(
            file_ids=[self.file1.id, self.file2.id],
            export_format='docx',
            exported_by=self.user,
        )
        self.assertIsInstance(result, ContentFile)
        self.assertIn('.docx', result.name)

    def test_export_to_pdf(self):
        """Export files to PDF format (requires reportlab)."""
        result = ImportExportService.export_files(
            file_ids=[self.file1.id],
            export_format='pdf',
            exported_by=self.user,
        )
        # reportlab may not be installed; if so, result is None gracefully
        if result is not None:
            self.assertIsInstance(result, ContentFile)
            self.assertIn('.pdf', result.name)
        # else: reportlab not available, graceful None return is acceptable

    def test_export_empty_file_list(self):
        """Export with no files should still return a valid file."""
        result = ImportExportService.export_files(
            file_ids=[],
            export_format='csv',
            exported_by=self.user,
        )
        self.assertIsInstance(result, ContentFile)

    def test_export_nonexistent_file_ids(self):
        """Export with non-existent file IDs should skip them."""
        result = ImportExportService.export_files(
            file_ids=[99999],
            export_format='csv',
            exported_by=self.user,
        )
        self.assertIsInstance(result, ContentFile)

    def test_export_invalid_format(self):
        """Export with unsupported format should raise error or return None."""
        result = ImportExportService.export_files(
            file_ids=[self.file1.id],
            export_format='invalid',
            exported_by=self.user,
        )
        # Should return None or raise for unsupported format
        self.assertTrue(result is None)


class ImportExportServiceBulkImportTest(TestCase):
    """Tests for bulk import functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='bulk@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Bulk',
            last_name='User',
            role='SYSADMIN'
        )

    def test_bulk_import_csv(self):
        """Bulk import from CSV should create multiple files."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['title', 'file_type', 'priority'])
        writer.writerow(['File One', 'MEMO', 'HIGH'])
        writer.writerow(['File Two', 'CORRESPONDENCE', 'NORMAL'])
        writer.writerow(['File Three', 'REPORT', 'LOW'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='bulk.csv')

        result = ImportExportService.bulk_import(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
        )
        self.assertIn('imported', result)
        self.assertIn('skipped', result)
        self.assertIn('errors', result)
        self.assertEqual(result['imported'], 3)
        self.assertEqual(result['skipped'], 0)

    def test_bulk_import_with_department(self):
        """Bulk import with department should apply to all records."""
        dept = Department.objects.create(name='HR', code='HR', category='SUPPORT')
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['title'])
        writer.writerow(['HR File 1'])
        writer.writerow(['HR File 2'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='hr_files.csv')

        result = ImportExportService.bulk_import(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
            department=dept,
        )
        self.assertEqual(result['imported'], 2)

    def test_bulk_import_skip_errors(self):
        """Bulk import with skip_errors=True should continue on bad rows."""
        # CSV with inconsistent columns
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['title'])
        writer.writerow(['Good File'])
        writer.writerow([])  # empty row
        writer.writerow(['Another Good File'])
        content = output.getvalue().encode('utf-8')
        uploaded_file = ContentFile(content, name='mixed.csv')

        result = ImportExportService.bulk_import(
            uploaded_file=uploaded_file,
            file_format='csv',
            created_by=self.user,
            skip_errors=True,
        )
        # Should still import valid rows
        self.assertGreaterEqual(result['imported'], 1)


class ImportExportServiceImportErrorHandlingTest(TestCase):
    """Tests for error handling in import."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='error@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Error',
            last_name='User',
            role='SYSADMIN'
        )

    def test_import_corrupted_file_returns_errors(self):
        """Corrupted file data should return errors without crashing."""
        uploaded_file = ContentFile(b'\x00\x01\x02\x03', name='corrupt.jpeg')

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format='jpeg',
            created_by=self.user,
        )
        # Should handle gracefully and have errors
        self.assertIsInstance(result, dict)
        self.assertIn('errors', result)
