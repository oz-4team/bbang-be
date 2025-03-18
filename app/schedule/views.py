from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.schedule.models import Schedule
from app.schedule.permissions import IsStaffPermission
from app.schedule.serializers import ScheduleSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    Schedule API
    """

    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsStaffPermission]
    lookup_field = "id"

    def get_queryset(self):
        artist_id = self.kwargs.get("artist_id")
        artist_group_id = self.kwargs.get("artist_group_id")

        if artist_id:
            return Schedule.objects.filter(artist_id=artist_id)
        elif artist_group_id:
            return Schedule.objects.filter(artist_group_id=artist_group_id)
        return Schedule.objects.all()

    def list(self, request, *args, **kwargs):
        """
        전체 일정 조회 (List)
        """
        queryset = self.get_queryset()
        serializer = ScheduleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        특정 일정 조회 (Retrieve)
        """
        schedule = self.get_object()
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        일정 수정 (Update)
        """
        schedule = self.get_object()  # ID로 일정 객체를 가져옵니다.
        serializer = self.get_serializer(schedule, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        일정 삭제 (Destroy)
        """
        schedule = self.get_object()
        schedule.delete()
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
