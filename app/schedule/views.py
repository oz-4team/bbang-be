import os
from decimal import ROUND_DOWN, Decimal

import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.content.models import Favorites
from app.schedule.models import Schedule
from app.schedule.serializers import (
    ScheduleSerializer,
)


def kakao_location(location):
    try:
        # 주소 검색 엔드포인트
        url_address = "https://dapi.kakao.com/v2/local/search/address.json"
        # 키워드 검색 엔드포인트
        url_keyword = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {"query": location}  # 검색할 위치 정보
        api_key = os.environ.get("KAKAO_CLIENT_ID")  # 환경 변수에서 API 키 가져오기
        if api_key and not api_key.startswith("KakaoAK"):
            api_key = "KakaoAK " + api_key  # API 키 앞에 접두사 추가  # 없으면 동작안함..
        headers = {"Authorization": api_key, "User-Agent": "bbang-app"}
        # 주소 검색을 시도
        response = requests.get(url_address, params=params, headers=headers)
        data = response.json()
        if data and data.get("documents"):
            document = data["documents"][0]
            if "address" in document:
                lon = document["address"]["x"]
                lat = document["address"]["y"]
                return lat, lon

        # 주소 검색 결과가 없으면 키워드 검색 시도
        response = requests.get(url_keyword, params=params, headers=headers)
        data = response.json()
        if data and data.get("documents"):
            document = data["documents"][0]
            lon = document["x"]
            lat = document["y"]
            return lat, lon

    except Exception as e:
        print("map error:", e)
    return None, None  # 오류나 결과가 없을 경우 None 반환


# 일반 유저 조회 API
class ScheduleListView(APIView):
    permission_classes = [AllowAny]  # 전체 일정 조회는 누구나

    def get(self, request):
        schedules = Schedule.objects.all()  # 일정 전체 가져오기
        serializer = ScheduleSerializer(schedules, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


class ArtistScheduleListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    def get(self, request, artist_id):
        schedules = Schedule.objects.filter(artist__id=artist_id)  # 아티스트 아이디로 일정 조회
        serializer = ScheduleSerializer(schedules, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


class ArtistGroupScheduleListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    def get(self, request, artist_group_id):
        schedules = Schedule.objects.filter(artist_group__id=artist_group_id)  # 아티스트 그룹 아이디로 일정 조회
        serializer = ScheduleSerializer(schedules, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    def get(self, request, schedule_id):
        schedule = get_object_or_404(Schedule, id=schedule_id)  # 일정 아이디로 일정 상세조회 없으면 404
        serializer = ScheduleSerializer(schedule)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


class FavoriteSchedulesView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자

    def get(self, request):
        user = request.user  # 유저 정보 가져옴
        favorites = Favorites.objects.filter(user=user)  # 유저가 즐겨찾기한 정보 가져옴
        schedules = [fav.schedule for fav in favorites if fav.schedule]  # 일정 리스트화
        serializer = ScheduleSerializer(schedules, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환


# 아티스트 일정 관리
class ArtistScheduleManageView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만(스태프)

    def post(self, request):
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
        if location:  # 주소로 kakao_locationAPi를 사용해 위도 경도 가져옴
            lat, lon = kakao_location(location)
            if lat and lon:
                # Decimal을 사용하여 7자리까지
                lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                request.data["latitude"] = str(lat)  # 위도 저장
                request.data["longitude"] = str(lon)  # 경도 저장

        request.data["artist"] = artist.id  # 아티스트 아이디 가져옴
        request.data["artist_group"] = None  # 아티스트 그룹 None처리

        serializer = ScheduleSerializer(data=request.data)  # 직렬화
        if serializer.is_valid():  # 유효하면
            schedule = serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # 직렬화 데이터 상태코드 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환

    def patch(self, request, schedule_id):
        user = request.user  # 유저 정보 가져옴
        if not user.is_staff:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

        schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)  # 일정 가져옴 업승면 404

        location = request.data.get("location", "").strip()  # 공백제거
        if location:
            lat, lon = kakao_location(location)
            if lat and lon:
                lat = Decimal(lat).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                lon = Decimal(lon).quantize(Decimal("0.0000000"), rounding=ROUND_DOWN)
                request.data["latitude"] = str(lat)
                request.data["longitude"] = str(lon)

        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)  # 직렬화
        if serializer.is_valid():  # 유효하면
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환

    def delete(self, request, schedule_id):
        user = request.user  # 유저정보 가져옴
        if not user.is_staff:  # 권한 없으면 예외처리
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

        schedule = get_object_or_404(Schedule, id=schedule_id, artist__isnull=False)
        schedule.delete()
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지, 상태코드 반환


# 아티스트 그룹 일정 관리
class ArtistGroupScheduleManageView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만(스태프)

    def post(self, request):
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

        serializer = ScheduleSerializer(data=request.data)  # 직렬화
        if serializer.is_valid():  # 유효하면
            schedule = serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # 직렬화 데이터 상태코드 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환

    def patch(self, request, schedule_id):
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

        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)  # 직렬화
        if serializer.is_valid():  # 유효하면
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화 데이터 상태코드 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러, 상태코드 반환

    def delete(self, request, schedule_id):
        user = request.user  # 유저정보 가져옴
        if not user.is_staff:  # 권한 없으면 예외처리
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  # 에러, 상태코드 반환

        schedule = get_object_or_404(Schedule, id=schedule_id, artist_group__isnull=False)  # 조회 없으면 404
        schedule.delete()  # 일정 삭제
        return Response({"message": "일정이 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지, 상태코드 반환
