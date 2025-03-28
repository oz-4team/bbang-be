import logging

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_extra_fields.fields import Base64ImageField

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

    @swagger_auto_schema(
        operation_summary="전체 좋아요 조회",
        operation_description="요청한 사용자가 생성한 모든 좋아요를 조회",
        responses={
            200: openapi.Response(
                description="좋아요 조회 성공",
                examples={
                    "application/json": [
                        {"like_id": 1, "artist": "아티스트 이름", "artist_group": "그룹명"}
                    ]
                }
            ),
            500: "서버 오류"
        }
    )
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

    @swagger_auto_schema(
        operation_summary="단건 좋아요 조회",
        operation_description="요청한 사용자가 생성한 특정 좋아요를 단건 조회",
        responses={
            200: openapi.Response(
                description="단건 좋아요 조회 성공",
                examples={
                    "application/json": {
                        "like_id": 1,
                        "artist": "아티스트 이름",
                        "artist_group": "그룹명"
                    }
                }
            ),
            500: "서버 오류"
        }
    )
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

    @swagger_auto_schema(
        operation_summary="좋아요 생성",
        operation_description="요청한 사용자가 아티스트나 아티스트 그룹에 좋아요를 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "artist_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="아티스트 ID"),
                "artist_group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="아티스트 그룹 ID")
            },
            required=[],
        ),
        responses={
            201: openapi.Response(
                description="좋아요 생성 성공",
                examples={"application/json": {"message": "좋아요가 생성되었습니다.", "like_id": 1}}
            ),
            400: "아티스트 또는 아티스트 그룹 선택 누락",
            500: "서버 오류"
        }
    )

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

    @swagger_auto_schema(
        operation_summary="좋아요 삭제",
        operation_description="요청한 사용자의 좋아요를 삭제합니다. 아티스트 ID나 아티스트 그룹 ID를 요청 데이터에서 전달받아 해당 좋아요를 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "artist_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="삭제할 아티스트 ID (선택)"),
                "artist_group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="삭제할 아티스트 그룹 ID (선택)")
            },
            # 필수값은 없지만 둘 중 하나는 전달되어야 합니다.
        ),
        responses={
            200: openapi.Response(
                description="좋아요 삭제 성공",
                examples={"application/json": {"message": "좋아요가 삭제되었습니다."}}
            ),
            400: "삭제할 항목 누락 또는 조건에 맞는 좋아요가 존재하지 않음",
            500: "서버 오류"
        }
    )
    def delete(self, request):
        try:
            user = request.user  # 요청 사용자
            # 요청 데이터에서 artist_id와 artist_group_id 추출
            artist_id = request.data.get("artist_id")
            artist_group_id = request.data.get("artist_group_id")

            # 둘 중 하나도 전달되지 않은 경우 에러 반환
            if not artist_id and not artist_group_id:
                return Response(
                    {"error": "삭제할 항목으로 아티스트 ID 또는 아티스트 그룹 ID를 전달해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # artist_id가 전달되면 해당 조건의 좋아요 조회
            if artist_id:
                like = get_object_or_404(Likes, artist__id=artist_id, user=user)
            else:
                # artist_group_id가 전달되면 해당 조건의 좋아요 조회
                like = get_object_or_404(Likes, artist_group__id=artist_group_id, user=user)

            # 좋아요 삭제
            like.delete()
            return Response({"message": "좋아요가 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # 예외 로깅
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 전체 즐겨찾기 조회 (사용자 기준)
class AllFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    @swagger_auto_schema(
        operation_summary="전체 즐겨찾기 조회",
        operation_description="요청한 사용자가 즐겨찾기한 모든 일정을 조회",
        responses={
            200: openapi.Response(
                description="즐겨찾기 일정 조회 성공",
                examples={"application/json": [
                    {"favorite_id": 1, "schedule_id": 10, "schedule_title": "일정 제목", "schedule_description": "일정 설명"}
                ]}
            ),
            500: "서버 오류"
        }
    )
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

    @swagger_auto_schema(
        operation_summary="즐겨찾기 생성",
        operation_description="요청한 사용자가 특정 일정에 대한 즐겨찾기를 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기할 일정 ID")
            },
            required=["schedule_id"],
        ),
        responses={
            201: openapi.Response(
                description="즐겨찾기 생성 성공",
                examples={"application/json": {"message": "즐겨찾기가 생성되었습니다.", "favorite_id": 1}}
            ),
            400: "일정 선택 누락 또는 이미 등록된 즐겨찾기",
            500: "서버 오류"
        }
    )
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
            # 이미 즐겨찾기가 존재하는지 체크
            if Favorites.objects.filter(user=user, schedule=schedule).exists():
                return Response(
                    {"error": "이미 해당 일정에 대한 즐겨찾기가 등록되어 있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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

    @swagger_auto_schema(
        operation_summary="즐겨찾기 삭제",
        operation_description="요청한 사용자가 즐겨찾기한 특정 일정을 삭제",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="삭제할 일정 ID")
            },
            required=["schedule_id"],
        ),
        responses={
            200: openapi.Response(
                description="즐겨찾기 삭제 성공",
                examples={"application/json": {"message": "즐겨찾기가 삭제되었습니다."}}
            ),
            400: "삭제할 일정 ID 누락",
            500: "서버 오류"
        }
    )
    def delete(self, request):
        try:
            user = request.user
            schedule_id = request.data.get("schedule_id")
            if not schedule_id:
                return Response(
                    {"error": "삭제할 일정 ID가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = get_object_or_404(Favorites, user=user, schedule__id=schedule_id)
            favorite.delete()
            return Response({"message": "즐겨찾기가 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            content_error.error(f"Content API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdvertisementListAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="광고 리스트 조회",
        operation_description="전체 광고 목록을 조회",
        responses={
            200: openapi.Response(
                description="광고 리스트 조회 성공",
                examples={"application/json": [
                    {
                        "id": 1,
                        "advertisement_type": "타입",
                        "status": True,
                        "sent_at": "2025-03-28T10:00:00Z",
                        "image_url": "http://example.com/image.jpg",
                        "link_url": "http://example.com",
                        "start_date": "2025-03-28T00:00:00Z",
                        "end_date": "2025-03-30T00:00:00Z"
                    }
                ]}
            ),
            500: "서버 오류"
        }
    )
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

    @swagger_auto_schema(
        operation_summary="광고 상세 조회",
        operation_description="특정 광고의 상세 정보를 조회",
        responses={
            200: openapi.Response(
                description="광고 상세 조회 성공",
                examples={"application/json": {
                    "id": 1,
                    "advertisement_type": "타입",
                    "status": True,
                    "sent_at": "2025-03-28T10:00:00Z",
                    "image_url": "http://example.com/image.jpg",
                    "link_url": "http://example.com",
                    "start_date": "2025-03-28T00:00:00Z",
                    "end_date": "2025-03-30T00:00:00Z"
                }}
            ),
            500: "서버 오류"
        }
    )
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
    permission_classes = [IsAdminUser]  # 관리자만 접근가능
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

    @swagger_auto_schema(
        operation_summary="광고 삭제",
        operation_description="관리자 권한을 가진 사용자가 특정 광고를 삭제",
        responses={
            200: openapi.Response(
                description="광고 삭제 성공",
                examples={"application/json": {"message": "광고가 삭제되었습니다."}}
            ),
            403: "권한 없음",
            500: "서버 오류"
        }
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
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # 이미지 업로드 지원
    @swagger_auto_schema(
        operation_summary="스태프 권한 신청",
        operation_description="로그인한 사용자가 스태프 권한 신청을 위해 필요한 정보를 전송하여 신청",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "artistName": openapi.Schema(type=openapi.TYPE_STRING, description="아티스트(개인, 그룹) 이름"),
                "artist_agency": openapi.Schema(type=openapi.TYPE_STRING, description="소속사"),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="전화번호"),
                "image_url": openapi.Schema(type=openapi.TYPE_STRING, description="첨부파일 (Base64 인코딩 문자열)"),
            },
            required=["artistName", "artist_agency", "phone_number", "image_url"],
        ),
        responses={
            201: openapi.Response(
                description="권한 신청 생성 성공",
                examples={"application/json": {"message": "권한 신청이 등록되었습니다.", "authority_id": 1}},
            ),
            400: "필수 항목 누락 또는 이미지 처리 오류",
            500: "서버 오류",
        },
    )
    def post(self, request):
        try:
            user = request.user  # 현재 로그인된 사용자
            data = request.data.copy()  # 유연하게 복사
            base64_field = Base64ImageField()
            base64_image = data.get("image_url")
            if base64_image:
                try:
                    data["image_url"] = base64_field.to_internal_value(base64_image)  # Base64 문자열을 이미지 파일 객체로 변환
                except Exception as e:
                    return Response({"error": "이미지 처리 중 오류 발생: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

            data["user"] = user.id  # 요청 유저 ID 설정

            artist_name = data.get("artistName")  # 아티스트 이름
            agency = data.get("artist_agency")  # 소속사
            phone = data.get("phone_number")  # 전화번호

            if not artist_name or not agency or not phone or not data.get("image_url"):
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
