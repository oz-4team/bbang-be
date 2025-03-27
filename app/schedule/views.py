import logging
from decimal import ROUND_DOWN, Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.artists.models import Artist, ArtistGroup
from app.content.models import Favorites
from app.schedule.models import Schedule
from app.schedule.serializers import ScheduleSerializer
from app.schedule.utiles import (
    Notification_likes_schedule_create_send,
    Notification_likes_schedule_delete_send,
    Notification_likes_schedule_update_send,
    kakao_location,
)

schedule_error = logging.getLogger("schedule")


class ScheduleListView(APIView):
    permission_classes = [AllowAny]


    def get(self, request):
        schedules = Schedule.objects.all()
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArtistScheduleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, artist_id):
        schedules = Schedule.objects.filter(artist__id=artist_id)
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArtistGroupScheduleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, artist_group_id):
        schedules = Schedule.objects.filter(artist_group__id=artist_group_id)
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        serializer = ScheduleSerializer(schedule, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArtistScheduleManageView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={201: ScheduleSerializer(), 400: "Bad Request", 403: "Forbidden"},
    )
    def post(self, request):
        try:
            user = request.user
            if not user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

            serializer = ScheduleSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                schedule = serializer.save()
                Notification_likes_schedule_create_send(schedule)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            schedule_error.error(f"Schedule API 에러 발생 {e}", exc_info=True)
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={200: ScheduleSerializer(), 400: "Bad Request", 403: "Forbidden"},
    )
    def patch(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            Notification_likes_schedule_update_send(schedule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)
        Notification_likes_schedule_delete_send(schedule, schedule.title)
        schedule.delete()
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)


class ArtistGroupScheduleManageView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={201: ScheduleSerializer(), 400: "Bad Request", 403: "Forbidden"},
    )
    def post(self, request):
        serializer = ScheduleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            schedule = serializer.save()
            Notification_likes_schedule_create_send(schedule)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={200: ScheduleSerializer(), 400: "Bad Request", 403: "Forbidden"},
    )
    def patch(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id, artist_group__isnull=False)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            Notification_likes_schedule_update_send(schedule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id, artist_group__isnull=False)
        Notification_likes_schedule_delete_send(schedule, schedule.title)
        schedule.delete()
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)
