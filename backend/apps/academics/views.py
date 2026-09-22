from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsAcademicStaff
from config.rbac import RoleBasedPermission, SchoolScopedQuerysetMixin

from .models import AcademicCalendar, Class, ClassSubject, Exam, ExamResult, GradeBoundary, GradingScale, ReportCard, StudentEnrollment, Subject
from .serializers import (
    AcademicCalendarSerializer,
    BulkMarkEntrySerializer,
    ClassListSerializer,
    ClassSerializer,
    ClassSubjectSerializer,
    ExamResultSerializer,
    ExamSerializer,
    GradeBoundarySerializer,
    GradingScaleSerializer,
    ReportCardSerializer,
    StudentEnrollmentSerializer,
    SubjectSerializer,
)


class ClassViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Class.objects.select_related("school", "class_teacher").all()
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["school", "level", "academic_year", "term", "is_active"]
    search_fields = ["name", "school__name"]
    ordering_fields = ["name", "level", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ClassListSerializer
        return ClassSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["category", "is_compulsory"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]


class ClassSubjectViewSet(viewsets.ModelViewSet):
    queryset = ClassSubject.objects.select_related("class_obj", "subject", "teacher").all()
    serializer_class = ClassSubjectSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["class_obj", "subject", "is_active"]


class ExamViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Exam.objects.select_related("school").all()
    serializer_class = ExamSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["school", "exam_type", "academic_year", "term", "is_active"]
    search_fields = ["name", "school__name"]
    ordering_fields = ["start_date", "created_at"]


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related("student__user", "exam", "subject", "entered_by").all()
    serializer_class = ExamResultSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["student", "exam", "subject"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    ordering_fields = ["marks_obtained", "entered_at"]

    @action(detail=False, methods=["post"], url_path="bulk-enter")
    def bulk_enter_marks(self, request):
        """Bulk enter marks for multiple students at once."""
        serializer = BulkMarkEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from decimal import Decimal
        from .models import Exam as ExamModel, Subject as SubjectModel

        try:
            exam = ExamModel.objects.get(id=serializer.validated_data["exam_id"])
        except ExamModel.DoesNotExist:
            return Response({"error": "Exam not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            subject = SubjectModel.objects.get(id=serializer.validated_data["subject_id"])
        except SubjectModel.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        results = []
        for entry in serializer.validated_data["marks"]:
            student_id = entry["student_id"]
            marks = Decimal(str(entry["marks_obtained"]))
            remark = entry.get("remark", "")

            result, created = ExamResult.objects.update_or_create(
                student_id=student_id,
                exam=exam,
                subject=subject,
                defaults={
                    "marks_obtained": marks,
                    "remark": remark,
                    "entered_by": request.user,
                },
            )
            results.append({
                "student_id": student_id,
                "result_id": result.id,
                "grade": result.grade,
                "created": created,
            })

        return Response({
            "message": f"Processed {len(results)} results.",
            "results": results,
        })


class ReportCardViewSet(viewsets.ModelViewSet):
    queryset = ReportCard.objects.select_related("student__user").all()
    serializer_class = ReportCardSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["student", "academic_year", "term", "is_released"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    ordering_fields = ["academic_year", "class_position"]


class AcademicCalendarViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = AcademicCalendar.objects.select_related("school").all()
    serializer_class = AcademicCalendarSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["school", "event_type", "academic_year"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "created_at"]


class StudentEnrollmentViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.select_related("student__user", "class_obj__school").all()
    serializer_class = StudentEnrollmentSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    school_filter_field = "class_obj__school"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["class_obj", "academic_year", "term", "status"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    ordering_fields = ["enrollment_date", "created_at"]


class GradingScaleViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = GradingScale.objects.select_related("school").prefetch_related("boundaries").all()
    serializer_class = GradingScaleSerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["school", "academic_year", "term", "is_active"]
    search_fields = ["name", "school__name"]
    ordering_fields = ["academic_year", "created_at"]


class GradeBoundaryViewSet(viewsets.ModelViewSet):
    queryset = GradeBoundary.objects.select_related("grading_scale").all()
    serializer_class = GradeBoundarySerializer
    rbac_app = "academics"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["grading_scale", "grade"]
