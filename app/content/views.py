# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from django.shortcuts import get_object_or_404
# from app.artists.models import Artist, ArtistGroup
# from app.content.models import Likes, Favorites, Notifications
# from app.schedule.models import Schedule
#
#
# class LikeAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         user = request.user
#         artist_id = request.data.get('artist_id')
#         artist_group_id = request.data.get('artist_group_id')
#
#         # 아티스트와 아티스트 그룹 둘 다 제공되지 않으면 에러 처리
#         if not artist_id and not artist_group_id:
#             return Response({'error': '아티스트나 아티스트 그룹을 선택해주세요.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         artist = None
#         artist_group = None
#         # artist_id가 있으면 해당 아티스트 객체 가져오기
#         if artist_id:
#             artist = get_object_or_404(Artist, id=artist_id)
#         # artist_group_id가 있으면 해당 아티스트 그룹 객체 가져오기
#         if artist_group_id:
#             artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
#
#         # 좋아요 객체 생성
#         like = Likes.objects.create(user=user, artist=artist, artist_group=artist_group)
#         # clean() 메서드 호출하여 유효성 검사
#         try:
#             like.clean()
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response({"message": "좋아요가 생성되었습니다.", "like_id": like.id},
#                         status=status.HTTP_201_CREATED)
#
#
# class FavoriteAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         user = request.user  # 사용자 가져오기
#         schedule_id = request.data.get('schedule_id')  # 일정 가져오기
#         if not schedule_id:  # 일정 id가 없으면 예외 처리
#             return Response({'error': '일정을 선택해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         schedule = get_object_or_404(Schedule, id=schedule_id)
#         # 수정: schedule 객체가 아니라 Favorites 모델을 사용하여 즐겨찾기 생성
#         favorite = Favorites.objects.create(user=user, schedule=schedule)
#         return Response({'message': "즐겨찾기가 생성되었습니다.", "favorite_id": favorite.id},
#                         status=status.HTTP_201_CREATED)
#
#
# class NotificationListAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user  # 사용자를 가져옴
#         like_notifications = Notifications.objects.filter(likes__user=user)  # likes를 통해 연결된 알림확인
#         favorite_notifications = Notifications.objects.filter(favorites__user=user)  # favorites를 통해 연결된 알림 확인
#         notifications = like_notifications | favorite_notifications
#         notifications = notifications.distinct()  # 중복 제거
#
#         # (실제 프로젝트에서는 직렬화 필요)
#         data = [{"id":n.id, "notifications":str(n)} for n in notifications]
#         return Response({"알림": data}, status=status.HTTP_200_OK)
#
# class ScheduleCreateNotificationAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         title = request.data.get("title")
#         description = request.data.get("description")
#         artist_id = request.data.get('artist_id')
#         artist_group_id = request.data.get('artist_group_id')
#
#         if not title:
#             return Response({'error':'제목을 입력하세요.'}, status=status.HTTP_400_BAD_REQUEST)
#         schedule = Schedule.objects.create(
#             title=title,
#             description=description
#         )
