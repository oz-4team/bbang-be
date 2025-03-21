from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from webpush import send_user_notification

from app.artists.models import Artist, ArtistGroup
from app.content.email import send_notification_email
from app.content.models import Favorites, Likes
from app.content.push import send_web_push_notification
from app.schedule.models import Schedule

# 전체 좋아요 조회 API
class AllLikesAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def get(self, request):
        user = request.user  # 사용자 정보 가져오기
        likes = Likes.objects.filter(user=user)  # 사용자의 모든 좋아요 데이터 가져오기
        response_data = [
            {
                "like_id": like.id,  # 각 좋아요의 ID
                "artist": like.artist.artist_name if like.artist else None,  # 좋아요 대상 아티스트의 이름
                "artist_group": like.artist_group.artist_group if like.artist_group else None,
                # 좋아요 대상 아티스트 그룹의 이름
                "artist_image": like.artist.image.image_url if like.artist and like.artist.image else None,  # 좋아요 대상 아티스트의 이미지 URL
                "artist_group_image": like.artist_group.image.image_url if like.artist_group and like.artist_group.image else None,  # 좋아요 대상 아티스트 그룹의 이미지 URL
            }
            for like in likes  # 리스트 컴프리헨션
        ]
        return Response(response_data, status=status.HTTP_200_OK)  # 결과를 JSON 형태로 반환


# 특정 좋아요 조회 API
class SingleLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def get(self, request, like_id):
        user = request.user  # 사용자 정보 가져오기
        like = get_object_or_404(Likes, id=like_id, user=user)  # 사용자의 특정 좋아요 데이터 가져오기
        response_data = {
            "like_id": like.id,  # 좋아요의 고유 ID
            "artist": like.artist.artist_name if like.artist else None,  # 아티스트 이름
            "artist_group": (
                like.artist_group.artist_group if like.artist_group else None
            ),  # 아티스트 그룹 이름  아티스트와 아티스트 그룹이 있으면 이름 없으면 None
            "artist_image": like.artist.image.image_url if like.artist and like.artist.image else None,  # 아티스트의 이미지 URL
            "artist_group_image": like.artist_group.image.image_url if like.artist_group and like.artist_group.image else None,  # 아티스트 그룹의 이미지 URL
        }
        return Response(response_data, status=status.HTTP_200_OK)  # 결과를 JSON 반환


# 좋아요 생성/삭제
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def post(self, request):  # 좋아요 생성
        user = request.user
        artist_id = request.data.get("artist_id")   # 아티스트 아이디를 받아옴
        artist_group_id = request.data.get("artist_group_id")  # 아티스트 그룹 아이디를 받아옴

        if not artist_id and not artist_group_id:   # 둘중에 하나 없으면 예외처리
            return Response({"error": "아티스트나 아티스트 그룹을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        artist = None  # 변수 설정
        artist_group = None  # 변수 설정
        if artist_id:   # 아티스트 아이디가 있으면 조회해 artist변수에 넣음
            artist = get_object_or_404(Artist, id=artist_id)    #
        if artist_group_id:  # 아티스트그룹 아이디가 있으면 조회해 artist_group변수에 넣음
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)

        like = Likes.objects.create(user=user, artist=artist, artist_group=artist_group)  #생성
        try:
            like.full_clean()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  # 에러 생길경우 에러와 상태코드 반환
        return Response({"message": "좋아요가 생성되었습니다.", "like_id": like.id}, status=status.HTTP_201_CREATED)  # 메세지와 상태코드

    def delete(self, request):  # 좋아요 삭제
        like_id = request.data.get("like_id")   # 좋아요 아이디 불러옴
        if not like_id:  # 좋아요 아이디 없으면 예외처리
            return Response({"error": "삭제할 좋아요가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        like = get_object_or_404(Likes, id=like_id, user=request.user)  # 좋아요 조회
        like.delete()  # 좋아요 삭제
        return Response({"message": "좋아요가 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지와 상태코드


# 전체 즐겨찾기 조회 API
class AllFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근

    def get(self, request):  # GET
        user = request.user  # 사용자 가져오기
        favorites = Favorites.objects.filter(user=user)  # 사용자의 모든 즐겨찾기 데이터 가져오기
        response_data = [
            {
                "favorite_id": favorite.id,  # 각 즐겨찾기의 고유 ID
                "schedule_title": favorite.schedule.title,  # 즐겨찾기에 연결된 스케줄의 제목
                "schedule_description": favorite.schedule.description,  # 즐겨찾기에 연결된 스케줄의 설명
            }
            for favorite in favorites  # 리스트 컴프리헨션
        ]
        return Response(response_data, status=status.HTTP_200_OK)  # 결과를 JSON 반환


# 특정 즐겨찾기 조회 API
class SingleFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근

    def get(self, request, favorite_id):  # get
        user = request.user  # 사용자 가져오기
        favorite = get_object_or_404(
            Favorites, id=favorite_id, user=user
        )  # 사용자와 일치하는 즐겨찾기 객체를 조회
        response_data = {
            "favorite_id": favorite.id,  # 즐겨찾기의 고유 ID
            "schedule_title": favorite.schedule.title,  # 즐겨찾기에 연결된 일정의 제목
            "schedule_description": favorite.schedule.description,  # 즐겨찾기에 연결된 일정의 설명
        }
        return Response(response_data, status=status.HTTP_200_OK)  # 결과를 JSON 반환


# 즐겨찾기 생성/삭제
class FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):  # 즐겨찾기 생성
        user = request.user  # 사용자 가져오기
        schedule_id = request.data.get("schedule_id")   # 일정 아이디 가져오기
        if not schedule_id:  # 일정 아이디 없으면 예외처리
            return Response({"error": "일정을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        schedule = get_object_or_404(Schedule, id=schedule_id)  # 일정 조회
        favorite = Favorites.objects.create(user=user, schedule=schedule)  # 즐겨찾기 생성
        return Response(  # 메세지 상태코드 반환
            {"message": "즐겨찾기가 생성되었습니다.", "favorite_id": favorite.id}, status=status.HTTP_201_CREATED
        )

    def delete(self, request):  # 즐겨찾기 삭제
        favorite_id = request.data.get("favorite_id")  # 즐겨찾기 아이디 가져오기
        if not favorite_id:  # 즐겨찾기 아이디 없으면 예외처리
            return Response({"error": "삭제할 즐겨찾기 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)  # 즐겨찾기 조회
        favorite.delete()  # 즐겨찾기 삭제
        return Response({"message": "즐겨찾기가 삭제되었습니다."}, status=status.HTTP_200_OK)  # 메세지 상태코드 반환


# 스케줄 생성 시 알림 및 이메일 전송
class ScheduleCreateNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 요청 데이터 추출
        title = request.data.get("title")  # 일정 제목
        description = request.data.get("description")  # 일정 설명
        artist_id = request.data.get("artist_id")  # 아티스트 ID
        artist_group_id = request.data.get("artist_group_id")  # 아티스트 그룹 ID

        if not title:
            return Response({"error": "일정 제목은 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 일정 생성 (현재 시간을 시작 및 종료 시간으로 사용)
        schedule = Schedule.objects.create(
            title=title,
            description=description,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        # 좋아요를 누른 사용자들을 찾기 위한 QuerySet
        like_qs = Likes.objects.all()
        notifications = []  # 이메일 전송할 정보를 담기 위한 리스트

        if artist_id:
            like_qs = like_qs.filter(artist__id=artist_id)
            for like in like_qs:
                payload = {
                    "head": "새 일정 등록",
                    "body": f"좋아요 하신 아티스트 {like.artist.artist_name if like.artist else '해당 아티스트'}의 새 일정 '{schedule.title}'이 등록되었습니다.",
                    "icon": "/static/img/notification-icon.png",  # 적절한 아이콘 URL
                    "url": f"https://yourdomain.com/schedule/{schedule.id}/"  # 클릭 시 이동 URL
                }
                send_user_notification(user=like.user, payload=payload, ttl=1000)
                # 이메일 전송 메시지 구성은 기존과 동일
                artist_name = like.artist.artist_name if like.artist else "해당 아티스트"
                message = f"좋아요 하신 아티스트 {artist_name}의 새 일정 '{schedule.title}'이 등록되었습니다."
                notifications.append({"email": like.user.email, "message": message})

        elif artist_group_id:
            like_qs = like_qs.filter(artist_group__id=artist_group_id)  # 아티스트 그룹 기준 필터링
            for like in like_qs:
                # 웹 푸시 알림 전송 함수 호출
                send_web_push_notification(
                    like.user,
                    f"새 일정 등록: {schedule.title} - 좋아요 하신 아티스트 그룹 {like.artist_group.artist_group if like.artist_group else '해당 그룹'}"
                )
                # 이메일 전송 메시지 구성
                group_name = like.artist_group.artist_group if like.artist_group else "해당 그룹"
                message = f"좋아요 하신 아티스트 그룹 {group_name}의 새 일정 '{schedule.title}'이 등록되었습니다."
                notifications.append({"email": like.user.email, "message": message})

        else:
            return Response(
                {"error": "아티스트 또는 아티스트 그룹을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 이메일을 별도의 루프로 전송
        for notification in notifications:
            send_notification_email("새 일정 등록 알림", notification["message"], [notification["email"]])

        return Response(
            {"message": "일정 등록 및 알림 전송 완료.", "schedule_id": schedule.id},
            status=status.HTTP_201_CREATED
        )


# 스케줄 수정 시 알림 및 이메일 전송
class ScheduleUpdateNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        schedule_id = request.data.get("schedule_id")  # 수정할 일정 ID
        new_title = request.data.get("title")  # 수정할 새 제목
        new_description = request.data.get("description")  # 수정할 새 설명

        if not schedule_id:
            return Response({"error": "일정 선택은 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 스케줄 조회 후 업데이트
        schedule = get_object_or_404(Schedule, id=schedule_id)
        if new_title:
            schedule.title = new_title
        if new_description:
            schedule.description = new_description
        schedule.save()

        favorites_qs = Favorites.objects.filter(schedule=schedule)  # 해당 일정 즐겨찾기한 사용자 조회
        notifications = []  # 이메일 전송할 정보를 담기 위한 리스트

        for favorite in favorites_qs:
            # 웹 푸시 알림 메시지 분기 처리
            if hasattr(schedule, "artist") and schedule.artist:
                name = schedule.artist.artist_name
                push_msg = f"수정된 일정: {schedule.title} - {name}님의 일정이 업데이트되었습니다."
                msg = f"즐겨찾기 하신 {name}님의 일정 '{schedule.title}'이 수정되었습니다."
            elif hasattr(schedule, "artist_group") and schedule.artist_group:
                name = schedule.artist_group.artist_group
                push_msg = f"수정된 일정: {schedule.title} - {name}의 일정이 업데이트되었습니다."
                msg = f"즐겨찾기 하신 {name}의 일정 '{schedule.title}'이 수정되었습니다."
            else:
                push_msg = f"수정된 일정: {schedule.title}이 업데이트되었습니다."
                msg = f"즐겨찾기 하신 일정 '{schedule.title}'이 수정되었습니다."
            # 웹 푸시 알림 전송
            send_web_push_notification(favorite.user, push_msg)
            notifications.append({"email": favorite.user.email, "message": msg})

        # 이메일을 별도의 루프로 전송
        for notification in notifications:
            send_notification_email("일정 수정 알림", notification["message"], [notification["email"]])

        return Response(
            {"message": "일정 수정 및 알림 전송 완료.", "schedule_id": schedule.id},
            status=status.HTTP_200_OK
        )