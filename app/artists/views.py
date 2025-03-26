import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.artists.serializers import ArtistGroupSerializer, ArtistSerializer
from app.content.models import Likes

artist_error = logging.getLogger("artist")


class ArtistAndGroupListView(APIView):  # 개별 아티스트와 그룹 아티스트를 동시에 조회
    permission_classes = [AllowAny]  # 인증된 사용자만 접근가능

    def get(self, request):
        try:
            artists = Artist.objects.all()  # 전체 개별 아티스트 조회
            artist_groups = ArtistGroup.objects.all()  # 전체 그룹 아티스트 조회

            user = request.user
            liked_artist_ids = set()
            liked_group_ids = set()

            # user가 인증된 상태라면 batch로 좋아요 데이터 미리 조회
            if user.is_authenticated:
                artist_ids = [a.id for a in artists]
                group_ids = [g.id for g in artist_groups]

                liked_artist_ids = set(
                    Likes.objects.filter(user=user, artist_id__in=artist_ids)
                                .values_list("artist_id", flat=True)
                )
                liked_group_ids = set(
                    Likes.objects.filter(user=user, artist_group_id__in=group_ids)
                                .values_list("artist_group_id", flat=True)
                )

            # context에 liked IDs를 담아서 전송
            context = {
                "request": request,
                "liked_artist_ids": liked_artist_ids,
                "liked_group_ids": liked_group_ids,
            }

            artist_serializer = ArtistSerializer(artists, many=True, context=context)
            artist_group_serializer = ArtistGroupSerializer(artist_groups, many=True, context=context)
            data = artist_serializer.data + artist_group_serializer.data
            return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArtistListView(APIView):  # 개별 아티스트 전체조회 및 생성

    def get_permissions(self):
        try:
            if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
                return [IsAuthenticated()]
            return [IsAdminUser()]
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            artists = Artist.objects.all()
            user = request.user
            liked_artist_ids = set()

            if user.is_authenticated:
                artist_ids = [a.id for a in artists]
                liked_artist_ids = set(
                    Likes.objects.filter(user=user, artist_id__in=artist_ids)
                                .values_list("artist_id", flat=True)
                )

            context = {
                "request": request,
                "liked_artist_ids": liked_artist_ids,
            }
            serializer = ArtistSerializer(artists, many=True, context=context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            data = request.data.copy()  # request.data를 mutable한 복사본 생성
            # 클라이언트에서 전달된 artist_group_id가 있다면 해당 그룹을 조회하여 할당
            artist_group_id = data.get("artist_group_id")
            if artist_group_id:
                artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
                data["artist_group"] = artist_group.id  # artist_group 필드에 그룹 ID 저장
            else:
                data["artist_group"] = None  # 그룹 정보가 없으면 None 설정

            serializer = ArtistSerializer(data=data, context={"request": request})  # 데이터를 ArtistSerializer에 입력하여 검증 준비
            if serializer.is_valid():  # 데이터 유효성 검사
                serializer.save()  # 유효한 경우 저장
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )  # 생성된 데이터를 201 CREATED 상태와 함께 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArtistDetailView(APIView):  # 개별 아티스트 상세조회, 수정, 삭제

    def get_permissions(self):
        try:
            if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
                return [IsAuthenticated()]
            return [IsAdminUser()]
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, artist_id):
        try:
            artist = get_object_or_404(Artist, id=artist_id)  # 지정한 ID의 아티스트 조회, 없으면 404 반환
            serializer = ArtistSerializer(artist, context={"request": request})  # 아티스트 데이터를 직렬화
            return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화된 데이터를 200 OK 상태와 함께 반환
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, artist_id):
        try:
            artist = get_object_or_404(Artist, id=artist_id)  # 수정할 아티스트 조회, 없으면 404 반환
            # 클라이언트에서 전달된 artist_group_id가 있으면 해당 그룹을 조회 후 업데이트
            artist_group_id = request.data.get("artist_group_id")
            if artist_group_id is not None:
                artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
                request.data["artist_group"] = artist_group.id  # artist_group 필드 업데이트
            else:
                request.data["artist_group"] = None  # 그룹 정보 삭제

            serializer = ArtistSerializer(artist, data=request.data, partial=True, context={"request": request})  # 부분 업데이트를 위한 직렬화
            if serializer.is_valid():  # 유효성 검사
                serializer.save()  # 변경 사항 저장
                return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터를 200 OK 상태와 함께 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환

        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, artist_id):
        try:
            artist = get_object_or_404(Artist, id=artist_id)  # 삭제할 아티스트 조회
            artist.delete()  # 아티스트 삭제
            return Response(
                {"message": "개별 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
            )  # 삭제 완료 메시지와 204 NO CONTENT 상태 반환
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArtistGroupListView(APIView):

    def get_permissions(self):
        try:
            if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
                return [IsAuthenticated()]
            return [IsAdminUser()]
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            artist_groups = ArtistGroup.objects.all()  # 전체 그룹 아티스트 조회
            user = request.user
            liked_group_ids = set()

            if user.is_authenticated:
                group_ids = [g.id for g in artist_groups]
                liked_group_ids = set(
                    Likes.objects.filter(user=user, artist_group_id__in=group_ids)
                                .values_list("artist_group_id", flat=True)
                )

            context = {
                "request": request,
                "liked_group_ids": liked_group_ids,
            }
            serializer = ArtistGroupSerializer(artist_groups, many=True, context=context)  # 데이터를 직렬화
            return Response(serializer.data, status=status.HTTP_200_OK)  # 200 OK 상태와 함께 데이터를 반환
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            serializer = ArtistGroupSerializer(data=request.data, context={"request": request})  # 입력된 데이터를 직렬화하여 검증 준비
            if serializer.is_valid():  # 데이터 유효성 검사
                serializer.save()  # 저장
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )  # 생성된 데이터를 201 CREATED 상태와 함께 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환

        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ArtistGroupMemberAddView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, group_id):
        artist_group = get_object_or_404(ArtistGroup, id=group_id)
        artist_ids = request.data.get("artist_ids")
        if not artist_ids:
            return Response({"error": "artist_ids가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        artists = Artist.objects.filter(id__in=artist_ids)
        for artist in artists:
            artist.artist_group = artist_group
            artist.save()

        return Response({"message": "아티스트 멤버가 그룹에 추가되었습니다."}, status=status.HTTP_200_OK)

class ArtistGroupMemberCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, group_id):
        artist_group = get_object_or_404(ArtistGroup, id=group_id)
        members_data = request.data.get("members")
        if not members_data:
            return Response({"error": "members 필드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        created_artists = []
        for member_data in members_data:
            member_data["artist_group"] = artist_group.id
            serializer = ArtistSerializer(data=member_data)
            if serializer.is_valid():
                artist = serializer.save()
                created_artists.append(artist)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = ArtistSerializer(created_artists, many=True).data
        return Response({"created_members": result}, status=status.HTTP_201_CREATED)


class ArtistGroupMemberDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, group_id, artist_id):
        artist_group = get_object_or_404(ArtistGroup, id=group_id)
        artist = get_object_or_404(Artist, id=artist_id)

        if artist.artist_group and artist.artist_group.id == artist_group.id:
            artist.artist_group = None  # 소속 해제
            artist.save()
            return Response({"message": "멤버가 그룹에서 삭제되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "해당 아티스트는 이 그룹에 속해 있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

class ArtistGroupDetailView(APIView):

    def get_permissions(self):
        try:
            if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
                return [IsAuthenticated()]
            return [IsAdminUser()]
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, artist_group_id):
        try:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 조회할 그룹 아티스트 조회
            serializer = ArtistGroupSerializer(artist_group, context={"request": request})  # 데이터를 직렬화
            return Response(serializer.data, status=status.HTTP_200_OK)  # 200 OK 상태와 함께 데이터를 반환
        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, artist_group_id):
        try:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 수정할 그룹 아티스트 조회
            serializer = ArtistGroupSerializer(
                artist_group, data=request.data, partial=True, context={"request": request}
            )  # 부분 업데이트를 위한 직렬화
            if serializer.is_valid():  # 유효성 검사
                serializer.save()  # 저장
                return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터를 200 OK 상태와 함께 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환

        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, artist_group_id):
        try:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 삭제할 그룹 아티스트 조회
            artist_group.delete()  # 그룹 삭제
            return Response(
                {"message": "그룹 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
            )  # 삭제 완료 메시지와 204 NO CONTENT 상태 반환

        except Exception as e:
            artist_error.error(f"Artist API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StaffArtistAndGroupListView(APIView):
    permission_classes = [IsAdminUser]  # Only authenticated users can access

    def get(self, request):
        user = request.user
        # 만약 staff가 아니면 403 반환
        if not user.is_staff:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # staff가 생성한 아티스트/아티스트그룹 필터링
        artists = Artist.objects.filter(created_by=user)
        artist_groups = ArtistGroup.objects.filter(created_by=user)

        # 직렬화
        artist_serializer = ArtistSerializer(artists, many=True, context={"request": request})
        artist_group_serializer = ArtistGroupSerializer(artist_groups, many=True, context={"request": request})

        return Response(
            {
                "artists": artist_serializer.data,
                "artist_groups": artist_group_serializer.data,
            },
            status=status.HTTP_200_OK
        )
