from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.content.email import send_notification_email
from app.content.models import Favorites, Likes, Notifications
from app.schedule.models import Schedule


# 좋아요
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근

    def post(self, request):  # 좋아요 생성
        user = request.user
        artist_id = request.data.get("artist_id")
        artist_group_id = request.data.get("artist_group_id")

        if not artist_id and not artist_group_id:
            return Response({"error": "아티스트나 아티스트 그룹을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        artist = None
        artist_group = None
        if artist_id:
            artist = get_object_or_404(Artist, id=artist_id)
        if artist_group_id:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)

        like = Likes.objects.create(user=user, artist=artist, artist_group=artist_group)
        try:
            like.full_clean()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "좋아요가 생성되었습니다.", "like_id": like.id}, status=status.HTTP_201_CREATED)

    def delete(self, request):  # 좋아요 삭제
        like_id = request.data.get("like_id")
        if not like_id:
            return Response({"error": "삭제할 좋아요 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        like = get_object_or_404(Likes, id=like_id, user=request.user)
        like.delete()
        return Response({"message": "좋아요가 삭제되었습니다."}, status=status.HTTP_200_OK)


# 즐겨찾기
class FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):  # 즐겨찾기 생성
        user = request.user
        schedule_id = request.data.get("schedule_id")
        if not schedule_id:
            return Response({"error": "일정을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        schedule = get_object_or_404(Schedule, id=schedule_id)
        favorite = Favorites.objects.create(user=user, schedule=schedule)
        return Response(
            {"message": "즐겨찾기가 생성되었습니다.", "favorite_id": favorite.id}, status=status.HTTP_201_CREATED
        )

    def delete(self, request):  # 즐겨찾기 삭제
        favorite_id = request.data.get("favorite_id")
        if not favorite_id:
            return Response({"error": "삭제할 즐겨찾기 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)
        favorite.delete()
        return Response({"message": "즐겨찾기가 삭제되었습니다."}, status=status.HTTP_200_OK)


# 스케줄 생성 시 알림 및 이메일 전송
class ScheduleCreateNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 요청 데이터 추출
        title = request.data.get("title")
        description = request.data.get("description")
        artist_id = request.data.get("artist_id")
        artist_group_id = request.data.get("artist_group_id")

        if not title:
            return Response({"error": "일정 제목은 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 일정 생성
        schedule = Schedule.objects.create(
            title=title,
            description=description,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        # 좋아요를 누른 사용자들을 찾기 위한 QuerySet
        like_qs = Likes.objects.all()
        if artist_id:
            like_qs = like_qs.filter(artist__id=artist_id)
            for like in like_qs:
                # 웹 내 알림 생성
                Notifications.objects.create(likes=like, is_active=True)
                artist_name = like.artist.artist_name if like.artist else "해당 아티스트"
                subject = "새 일정 등록 알림"
                message = f"좋아요 하신 아티스트 {artist_name}의 새 일정 '{schedule.title}'이 등록되었습니다."
                recipient_list = [like.user.email]
                send_notification_email(subject, message, recipient_list)
            return Response(
                {"message": "일정 등록 및 알림 전송 완료.", "schedule_id": schedule.id}, status=status.HTTP_201_CREATED
            )

        elif artist_group_id:
            like_qs = like_qs.filter(artist_group__id=artist_group_id)
            for like in like_qs:
                Notifications.objects.create(likes=like, is_active=True)
                group_name = like.artist_group.artist_group if like.artist_group else "해당 그룹"
                subject = "새 일정 등록 알림"
                message = f"좋아요 하신 아티스트 그룹 {group_name}의 새 일정 '{schedule.title}'이 등록되었습니다."
                recipient_list = [like.user.email]
                send_notification_email(subject, message, recipient_list)
            return Response(
                {"message": "일정 등록 및 알림 전송 완료.", "schedule_id": schedule.id}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "아티스트 또는 아티스트 그룹을 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )


# 스케줄 수정 시 알림 및 이메일 전송
class ScheduleUpdateNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        schedule_id = request.data.get("schedule_id")
        new_title = request.data.get("title")
        new_description = request.data.get("description")

        if not schedule_id:
            return Response({"error": "일정 선택은 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        schedule = get_object_or_404(Schedule, id=schedule_id)
        if new_title:
            schedule.title = new_title
        if new_description:
            schedule.description = new_description
        schedule.save()

        favorites_qs = Favorites.objects.filter(schedule=schedule)
        for favorite in favorites_qs:
            Notifications.objects.create(favorites=favorite, is_active=True)
            # 스케줄 객체에 연결된 아티스트 또는 아티스트 그룹 정보에 따라 메시지 분기
            if hasattr(schedule, "artist") and schedule.artist:
                name = schedule.artist.artist_name
                msg = f"즐겨찾기 하신 {name}님의 일정 '{schedule.title}'이 수정되었습니다."
            elif hasattr(schedule, "artist_group") and schedule.artist_group:
                name = schedule.artist_group.artist_group
                msg = f"즐겨찾기 하신 {name}의 일정 '{schedule.title}'이 수정되었습니다."
            else:
                msg = f"즐겨찾기 하신 일정 '{schedule.title}'이 수정되었습니다."
            subject = "일정 수정 알림"
            recipient_list = [favorite.user.email]
            send_notification_email(subject, msg, recipient_list)

        return Response(
            {"message": "일정 수정 및 알림 전송 완료.", "schedule_id": schedule.id}, status=status.HTTP_200_OK
        )
