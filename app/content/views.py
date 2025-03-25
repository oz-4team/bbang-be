import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.content.models import (  # 권한 신청 모델 import
    Advertisement,
    Favorites,
    Likes,
    authority,
)
from app.schedule.models import Schedule

content_error = logging.getLogger("content")


# 전체 좋아요 조회 (사용자 기준)
class AllLikesAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def get(self, request):
        try:
            user = request.user  # 요청한 사용자 정보 가져오기
            likes = Likes.objects.filter(user=user)  # 해당 사용자가 생성한 모든 좋아요 조회
            # 좋아요 정보를 리스트 형태로 구성
            response_data = [
                {
                    "like_id": like.id,  # 좋아요 고유 ID
                    "artist": like.artist.artist_name if like.artist else None,  # 아티스트 이름 (있으면)
                    "artist_group": like.artist_group.artist_group if like.artist_group else None,  # 그룹명 (있으면)
                }
                for like in likes
            ]
            return Response(response_data, status=status.HTTP_200_OK)  # 결과 반환
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 특정 좋아요 조회 (단건 조회)
class SingleLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def get(self, request, like_id):
        try:
            user = request.user  # 요청 사용자
            like = get_object_or_404(Likes, id=like_id, user=user)  # 해당 사용자에 속한 좋아요 단건 조회
            response_data = {
                "like_id": like.id,
                "artist": like.artist.artist_name if like.artist else None,
                "artist_group": like.artist_group.artist_group if like.artist_group else None,
            }
            return Response(response_data, status=status.HTTP_200_OK)  # 데이터 반환 상태코드
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 좋아요 생성 및 삭제 API
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def post(self, request):
        try:
            user = request.user  # 요청 사용자
            # 클라이언트로부터 아티스트 또는 아티스트 그룹 ID를 가져옴
            artist_id = request.data.get("artist_id")
            artist_group_id = request.data.get("artist_group_id")
            # 두 값 모두 없으면 에러 반환
            if not artist_id and not artist_group_id:
                return Response(
                    {"error": "아티스트나 아티스트 그룹을 선택해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # 아티스트와 아티스트 그룹 조회 (있으면)
            artist = get_object_or_404(Artist, id=artist_id) if artist_id else None
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id) if artist_group_id else None
            # 좋아요 객체 생성
            like = Likes.objects.create(user=user, artist=artist, artist_group=artist_group)
            # 모델의 clean() 호출하여 유효성 검사 (예외 발생 시 처리)
            try:
                like.full_clean()
            except Exception as e:  # 예외처리
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(  # 메시지 상태반환
                {"message": "좋아요가 생성되었습니다.", "like_id": like.id},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        try:
            # 좋아요 삭제를 위한 ID를 요청 데이터에서 가져옴
            like_id = request.data.get("like_id")
            if not like_id:  # 좋아요 아이디가 없으면
                return Response(  # 예외처리
                    {"error": "삭제할 좋아요 ID가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            like = get_object_or_404(Likes, id=like_id, user=request.user)  # 조회
            like.delete()  # 좋아요 삭제
            return Response({"message": "좋아요가 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메시지 상태코드
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 전체 즐겨찾기 조회 (사용자 기준)
class AllFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def get(self, request):
        try:
            user = request.user  # 요청 사용자
            favorites = Favorites.objects.filter(user=user)  # 사용자가 즐겨찾기한 모든 일정 조회
            response_data = [
                {
                    "favorite_id": fav.id,
                    "schedule_id": fav.schedule.id,
                    "schedule_title": fav.schedule.title,
                    "schedule_description": fav.schedule.description,
                }
                for fav in favorites
            ]
            return Response(response_data, status=status.HTTP_200_OK)  # 결과반환, 상태반환
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# 즐겨찾기 생성 및 삭제 API
class FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def post(self, request):
        try:
            user = request.user  # 요청 사용자
            schedule_id = request.data.get("schedule_id")  # 아이디 추출
            if not schedule_id:  # 없으면 예외처리
                return Response(
                    {"error": "일정을 선택해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            schedule = get_object_or_404(Schedule, id=schedule_id)  # 조회 없으면 404
            favorite = Favorites.objects.create(user=user, schedule=schedule)  # 즐겨찾기 생성
            return Response(  # 메세지 상태코드
                {"message": "즐겨찾기가 생성되었습니다.", "favorite_id": favorite.id},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        try:
            favorite_id = request.data.get("favorite_id")  # 아이디 추출
            if not favorite_id:
                return Response(  # 없으면 예외처리
                    {"error": "삭제할 즐겨찾기 ID가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)  # 조회
            favorite.delete()  # 삭제
            return Response({"message": "즐겨찾기가 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지 상태코드
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvertisementListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            ads = Advertisement.objects.all()
            data = [
                {
                    "id": ad.id,
                    "advertisement_type": ad.advertisement_type,
                    "status": ad.status,
                    "sent_at": ad.sent_at,
                    "image_url": ad.image_url.url if ad.image_url else None,
                    "link_url": ad.link_url,
                    "start_date": ad.start_date,
                    "end_date": ad.end_date,
                }
                for ad in ads
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvertisementDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, advertisement_id):
        try:
            ad = get_object_or_404(Advertisement, id=advertisement_id)
            data = {
                "id": ad.id,
                "advertisement_type": ad.advertisement_type,
                "status": ad.status,
                "sent_at": ad.sent_at,
                "image_url": ad.image_url.url if ad.image_url else None,
                "link_url": ad.link_url,
                "start_date": ad.start_date,
                "end_date": ad.end_date,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvertisementManageAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근
    parser_classes = (MultiPartParser, FormParser)  # 이미지 업로드를 위한 파서

    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

            data = request.data
            ad = Advertisement.objects.create(
                advertisement_type=data.get("advertisement_type"),
                status=data.get("status", False),
                sent_at=data.get("sent_at"),
                image_url=data.get("image_url"),
                link_url=data.get("link_url"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
            )
            return Response(
                {"message": "광고가 생성되었습니다.", "advertisement_id": ad.id}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, advertisement_id):
        try:
            if not request.user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

            ad = get_object_or_404(Advertisement, id=advertisement_id)
            data = request.data

            for field in ["advertisement_type", "status", "sent_at", "image_url", "link_url", "start_date", "end_date"]:
                if field in data:
                    setattr(ad, field, data.get(field))

            ad.save()
            return Response({"message": "광고가 수정되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, advertisement_id):
        try:
            if not request.user.is_staff:
                return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

            ad = get_object_or_404(Advertisement, id=advertisement_id)
            ad.delete()
            return Response({"message": "광고가 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StaffUpAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인 사용자만 접근 가능
    parser_classes = (MultiPartParser, FormParser)  # 이미지 업로드 지원

    def post(self, request):
        try:
            user = request.user  # 현재 로그인된 사용자
            data = request.data.copy()  # 유연하게 복사
            data["user"] = user.id  # 요청 유저 ID 설정

            artist_name = data.get("artistName")  # 아티스트 이름
            agency = data.get("artist_agency")  # 소속사
            phone = data.get("phone_number")  # 전화번호

            if not artist_name or not agency or not phone:
                return Response(  # 셋중 하나라도 없으면 예외처리
                    {"error": "필수 항목이 누락되었습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            authority_obj = authority.objects.create(  # 권한 신청 생성
                artistName=artist_name,
                artist_agency=agency,
                user=user,
                phone_number=phone,
                image_url=data.get("image_url"),
            )

            return Response(
                {"message": "권한 신청이 등록되었습니다.", "authority_id": authority_obj.id},  # 메세지 반환, 상태코드
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
