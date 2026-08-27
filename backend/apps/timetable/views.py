from rest_framework import permissions, viewsets

from config.permissions import IsAcademicStaff

from .models import Period, TeacherTimetable, Timetable, TimetableEntry
from .serializers import PeriodSerializer, TeacherTimetableSerializer, TimetableEntrySerializer, TimetableSerializer


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.select_related("school").all()
    serializer_class = PeriodSerializer
    permission_classes = [IsAcademicStaff]
    filterset_fields = ["school", "is_break", "is_active"]
    ordering_fields = ["period_number"]


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related("school", "class_obj").all()
    serializer_class = TimetableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["school", "class_obj", "academic_year", "term", "is_active"]
    ordering_fields = ["academic_year", "created_at"]


class TimetableEntryViewSet(viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.select_related("timetable", "period", "subject", "teacher").all()
    serializer_class = TimetableEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["timetable", "day", "subject", "teacher"]
    ordering_fields = ["day", "period"]


class TeacherTimetableViewSet(viewsets.ModelViewSet):
    queryset = TeacherTimetable.objects.select_related("teacher", "timetable").all()
    serializer_class = TeacherTimetableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["teacher", "timetable"]
