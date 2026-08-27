from rest_framework import permissions, viewsets

from config.permissions import IsAdminOrTGOrDeptHead

from .models import FrenchClub, FrenchClubMember, FrenchCompetition, FrenchProgram
from .serializers import (
    FrenchClubMemberSerializer,
    FrenchClubSerializer,
    FrenchCompetitionSerializer,
    FrenchProgramSerializer,
)


class FrenchProgramViewSet(viewsets.ModelViewSet):
    queryset = FrenchProgram.objects.all()
    serializer_class = FrenchProgramSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["level", "is_active"]
    search_fields = ["name", "description"]


class FrenchClubViewSet(viewsets.ModelViewSet):
    queryset = FrenchClub.objects.select_related("school", "coordinator").all()
    serializer_class = FrenchClubSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["school", "is_active"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class FrenchClubMemberViewSet(viewsets.ModelViewSet):
    queryset = FrenchClubMember.objects.select_related("club", "student__user").all()
    serializer_class = FrenchClubMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["club", "student", "is_active"]


class FrenchCompetitionViewSet(viewsets.ModelViewSet):
    queryset = FrenchCompetition.objects.all()
    serializer_class = FrenchCompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["level", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["date", "created_at"]
