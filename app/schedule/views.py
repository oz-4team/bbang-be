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


# 일반 유저 조회 API
class ScheduleListView(APIView):
    permission_classes = [AllowAny]  # 전체 일정 조회는 누구나

    @swagger_auto_schema(
        operation_summary="전체 일정 조회",
        operation_description="전체 일정을 조회(모든 사용자가 접근 가능)",
        responses={
            200: openapi.Response(
                description="일정 조회 성공",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "is_active": True,
                            "title": "일정 제목",
                            "description": "일정 설명",
                            "start_date": "2025-03-28T10:00:00Z",
                            "end_date": "2025-03-28T12:00:00Z",
                            "location": "고척스카이돔",
                            "latitude": "37.5665350",
                            "longitude": "126.9779690",
                            "user": 1,
                            "artist": None,
                            "artist_id": None,
                            "artist_group": None,
                            "artist_group_id": None,
                            "is_favorited": False,
                            "image_url": "http://example.com/schedule/image.jpg"
                        }
                    ]
                }
            ),
            500: "서버 오류"
        },
    )
    def get(self, request):
        schedules = Schedule.objects.all()  # 일정 전체 가져오기
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 아티스트 아이디로 일정 조회 API
class ArtistScheduleListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    @swagger_auto_schema(
        operation_summary="아티스트 일정 조회",
        operation_description="특정 아티스트 아이디에 해당하는 일정을 조회",
        responses={
            200: openapi.Response(
                description="아티스트 일정 조회 성공",
                examples={"application/json": [
                    # ScheduleSerializer 데이터 예시
                ]},
            ),
            500: "서버 오류"
        },
    )
    def get(self, request, artist_id):
        schedules = Schedule.objects.filter(artist__id=artist_id)  # 아티스트 아이디로 일정 조회
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 아티스트 그룹 아이디로 일정 조회 API
class ArtistGroupScheduleListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    @swagger_auto_schema(
        operation_summary="아티스트 그룹 일정 조회",
        operation_description="특정 아티스트 그룹 아이디에 해당하는 일정을 조회",
        responses={
            200: openapi.Response(
                description="아티스트 그룹 일정 조회 성공",
                examples={"application/json": [
                    # ScheduleSerializer 데이터 예시
                ]},
            ),
            500: "서버 오류"
        },
    )
    def get(self, request, artist_group_id):
        schedules = Schedule.objects.filter(artist_group__id=artist_group_id)  # 아티스트 그룹 아이디로 일정 조회
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 일정 상세 조회 API
class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    @swagger_auto_schema(
        operation_summary="일정 상세 조회",
        operation_description="특정 일정 아이디에 해당하는 일정의 상세 정보를 조회",
        responses={
            200: openapi.Response(
                description="일정 상세 조회 성공",
                examples={"application/json": {
                    # ScheduleSerializer 단일 데이터 예시
                }},
            ),
            404: "일정 없음",
            500: "서버 오류"
        },
    )
    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)  # 일정 아이디로 일정 상세조회 없으면 404
        serializer = ScheduleSerializer(schedule, context={"request": request})  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 즐겨찾기한 일정 조회 API
class FavoriteSchedulesView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    @swagger_auto_schema(
        operation_summary="즐겨찾기 일정 조회",
        operation_description="요청한 사용자가 즐겨찾기한 모든 일정을 조회",
        responses={
            200: openapi.Response(
                description="즐겨찾기 일정 조회 성공",
                examples={"application/json": [
                    # ScheduleSerializer 데이터 예시
                ]},
            ),
            500: "서버 오류"
        },
    )
    def get(self, request):
        user = request.user  # 유저 정보 가져옴
        favorites = Favorites.objects.filter(user=user)  # 유저가 즐겨찾기한 정보 가져옴
        schedules = [fav.schedule for fav in favorites if fav.schedule]  # 일정 리스트화
        serializer = ScheduleSerializer(schedules, many=True, context={"request": request})  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 아티스트 일정 관리 API (생성, 수정, 삭제)
class ArtistScheduleManageView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만(스태프)

    @swagger_auto_schema(
        operation_summary="아티스트 일정 생성",
        operation_description="관리자 권한을 가진 사용자가 아티스트 일정을 생성(주소 입력 시 kakao_location API를 통해 위도, 경도 자동설정)",
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response(
                description="일정 생성 성공",
                examples={"application/json": {
                    # 생성된 ScheduleSerializer 데이터 예시
                }},
            ),
            400: "필수 필드 누락",
            403: "권한 없음",
            500: "서버 오류",
        },
    )
    def post(self, request):
        try:
            user = request.user  # 유저 정보 가져옴
            if not user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

            artist_id = request.data.get("artist_id")  # 아티스트 아이디 가져옴
            if not artist_id:  # 아티스트 아이디 없으면 예외
                return Response(
                    {"error": "아티스트 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
                )  # 에러, 상태코드 반환
            artist = get_object_or_404(Artist, id=artist_id)  # 아티스트 조회 없으면 404

            location = request.data.get("location", "").strip()  # 문자열 공백제거
            if location:  # 주소로 kakao_location API를 사용해 위도 경도 가져옴
                lat, lon = kakao_location(location)
                if lat and lon:
                    # Decimal을 사용하여 7자리까지
                    lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    request.data["latitude"] = str(lat)  # 위도 저장
                    request.data["longitude"] = str(lon)  # 경도 저장

            request.data["artist"] = artist.id  # 아티스트 아이디 가져옴
            request.data["artist_group"] = None  # 아티스트 그룹 None처리

            serializer = ScheduleSerializer(data=request.data, context={"request": request})  # 직렬화
            if serializer.is_valid():  # 유효하면
                schedule = serializer.save()  # 저장
                Notification_likes_schedule_create_send(schedule)
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # 직렬화 데이터 상태코드 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환
        except Exception as e:
            schedule_error.error(f"Schedule API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="아티스트 일정 수정",
        operation_description="관리자 권한을 가진 사용자가 아티스트 일정을 수정(주소 입력 시 kakao_location API를 통해 위도, 경도 자동업데이트)",
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response(
                description="일정 수정 성공",
                examples={"application/json": {
                    # 수정된 ScheduleSerializer 데이터 예시
                }},
            ),
            400: "유효성 검사 실패",
            403: "권한 없음",
            500: "서버 오류"
        },
    )
    def patch(self, request, schedule_id):
        try:
            user = request.user  # 유저 정보 가져옴
            if not user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

            schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)  # 일정 가져옴, 없으면 404

            location = request.data.get("location", "").strip()  # 공백제거
            if location:
                lat, lon = kakao_location(location)
                if lat and lon:
                    lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    request.data["latitude"] = str(lat)
                    request.data["longitude"] = str(lon)

            serializer = ScheduleSerializer(
                schedule, data=request.data, partial=True, context={"request": request}
            )  # 직렬화
            if serializer.is_valid():  # 유효하면
                serializer.save()  # 저장
                Notification_likes_schedule_update_send(schedule)
                return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환
        except Exception as e:
            schedule_error.error(f"Schedule API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="아티스트 일정 삭제",
        operation_description="관리자 권한을 가진 사용자가 아티스트 일정을 삭제",
        responses={
            200: openapi.Response(
                description="일정 삭제 성공",
                examples={"application/json": {"message": "일정이 삭제되었습니다."}},
            ),
            403: "권한 없음",
            500: "서버 오류"
        },
    )
    def delete(self, request, schedule_id):
        user = request.user  # 유저정보 가져옴
        if not user.is_staff:  # 권한 없으면 예외처리
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

        schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)
        Notification_likes_schedule_delete_send(schedule, schedule.title)
        schedule.delete()  # 일정 삭제
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지, 상태코드 반환


# 아티스트 그룹 일정 관리 API (생성, 수정, 삭제)
class ArtistGroupScheduleManageView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만(스태프)

    @swagger_auto_schema(
        operation_summary="아티스트 그룹 일정 생성",
        operation_description="관리자 권한을 가진 사용자가 아티스트 그룹 일정을 생성 (주소 입력 시 kakao_location API를 통해 위도, 경도 자동설정)",
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response(
                description="일정 생성 성공",
                examples={"application/json": {
                    # 생성된 ScheduleSerializer 데이터 예시
                }},
            ),
            400: "필수 필드 누락",
            403: "권한 없음",
            500: "서버 오류",
        },
    )
    def post(self, request):
        try:
            user = request.user  # 유저정보 가져옴
            if not user.is_staff:  # 권한 없으면 예외처리
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

            artist_group_id = request.data.get("artist_group_id")  # 아티스트 그룹 아이디 가져옴
            if not artist_group_id:
                return Response(
                    {"error": "아티스트 그룹 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
                )  # 에러, 상태코드 반환
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 조회 없으면 404

            location = request.data.get("location", "").strip()  # 공백제거
            if location:
                lat, lon = kakao_location(location)
                if lat and lon:
                    lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    request.data["latitude"] = str(lat)
                    request.data["longitude"] = str(lon)

            request.data["artist_group"] = artist_group.id
            request.data["artist"] = None

            serializer = ScheduleSerializer(data=request.data, context={"request": request})  # 직렬화
            if serializer.is_valid():  # 유효하면
                schedule = serializer.save()  # 저장
                Notification_likes_schedule_create_send(schedule)
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # 직렬화 데이터 상태코드 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환
        except Exception as e:
            schedule_error.error(f"Schedule API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="아티스트 그룹 일정 수정",
        operation_description="관리자 권한을 가진 사용자가 아티스트 그룹 일정을 수정(주소 입력 시 kakao_location API를 통해 위도, 경도 자동업데이트)",
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response(
                description="일정 수정 성공",
                examples={"application/json": {
                    # 수정된 ScheduleSerializer 데이터 예시
                }},
            ),
            400: "유효성 검사 실패",
            403: "권한 없음",
            500: "서버 오류"
        },
    )
    def patch(self, request, schedule_id):
        try:
            user = request.user  # 유저정보 가져옴
            if not user.is_staff:  # 권한 없으면 예외처리
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

            schedule = get_object_or_404(Schedule, id=schedule_id, artist_group__isnull=False)  # 조회 없으면 404

            location = request.data.get("location", "").strip()  # 공백제거
            if location:
                lat, lon = kakao_location(location)
                if lat and lon:
                    lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                    request.data["latitude"] = str(lat)
                    request.data["longitude"] = str(lon)

            serializer = ScheduleSerializer(
                schedule, data=request.data, partial=True, context={"request": request}
            )  # 직렬화
            if serializer.is_valid():  # 유효하면
                serializer.save()  # 저장
                Notification_likes_schedule_update_send(schedule)
                return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환
        except Exception as e:
            schedule_error.error(f"Schedule API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="아티스트 그룹 일정 삭제",
        operation_description="관리자 권한을 가진 사용자가 아티스트 그룹 일정을 삭제",
        responses={
            200: openapi.Response(
                description="일정 삭제 성공",
                examples={"application/json": {"message": "일정이 삭제되었습니다."}},
            ),
            403: "권한 없음",
            500: "서버 오류"
        },
    )
    def delete(self, request, schedule_id):
        user = request.user  # 유저정보 가져옴
        if not user.is_staff:  # 권한 없으면 예외처리
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환
        schedule = get_object_or_404(Schedule, id=schedule_id, artist_group__isnull=False)  # 조회 없으면 404
        Notification_likes_schedule_delete_send(schedule, schedule.title)
        schedule.delete()  # 일정 삭제
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지, 상태코드 반환