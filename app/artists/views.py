from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.artists.serializers import ArtistGroupSerializer, ArtistSerializer


class ArtistAndGroupListView(APIView):  # 개별 아티스트와 그룹 아티스트를 동시에 조회
    permission_classes = [AllowAny]  # 인증된 사용자만 접근가능

    def get(self, request):
        artists = Artist.objects.all()  # 전체 개별 아티스트 조회
        artist_groups = ArtistGroup.objects.all()  # 전체 그룹 아티스트 조회
        artist_serializer = ArtistSerializer(artists, many=True)  # 개별 아티스트 데이터를 직렬화
        artist_group_serializer = ArtistGroupSerializer(artist_groups, many=True)  # 그룹 아티스트 데이터를 직렬화
        data = artist_serializer.data + artist_group_serializer.data  # 개별 아티스트와 그룹 아티스트 데이터를 하나의 리스트로 병합
        return Response(
            {"data": data},  # 병합된 데이터를 'data' 키로 반환
            status=status.HTTP_200_OK,  # 200 OK 상태 코드 반환
        )  # 200 OK 상태 코드 반환


class ArtistListView(APIView):  # 개별 아티스트 전체조회 및 생성

    def get_permissions(self):
        if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        artists = Artist.objects.all()  # 전체 아티스트 조회
        serializer = ArtistSerializer(artists, many=True)  # 데이터를 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화된 데이터를 200 OK 상태와 함께 반환

    def post(self, request):
        data = request.data.copy()  # request.data를 mutable한 복사본 생성
        # 클라이언트에서 전달된 artist_group_id가 있다면 해당 그룹을 조회하여 할당
        artist_group_id = data.get("artist_group_id")
        if artist_group_id:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
            data["artist_group"] = artist_group.id  # artist_group 필드에 그룹 ID 저장
        else:
            data["artist_group"] = None  # 그룹 정보가 없으면 None 설정

        serializer = ArtistSerializer(data=data)  # 데이터를 ArtistSerializer에 입력하여 검증 준비
        if serializer.is_valid():  # 데이터 유효성 검사
            serializer.save()  # 유효한 경우 저장
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )  # 생성된 데이터를 201 CREATED 상태와 함께 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환


class ArtistDetailView(APIView):  # 개별 아티스트 상세조회, 수정, 삭제

    # def get_permissions(self):
    #     if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
    #         return [IsAuthenticated()]
    #     return [IsAdminUser()]

    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)  # 지정한 ID의 아티스트 조회, 없으면 404 반환
        serializer = ArtistSerializer(artist)  # 아티스트 데이터를 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화된 데이터를 200 OK 상태와 함께 반환

    def patch(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)  # 수정할 아티스트 조회, 없으면 404 반환
        # 클라이언트에서 전달된 artist_group_id가 있으면 해당 그룹을 조회 후 업데이트
        artist_group_id = request.data.get("artist_group_id")
        if artist_group_id is not None:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
            request.data["artist_group"] = artist_group.id  # artist_group 필드 업데이트
        else:
            request.data["artist_group"] = None  # 그룹 정보 삭제

        serializer = ArtistSerializer(artist, data=request.data, partial=True)  # 부분 업데이트를 위한 직렬화
        if serializer.is_valid():  # 유효성 검사
            serializer.save()  # 변경 사항 저장
            return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터를 200 OK 상태와 함께 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환

    def delete(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)  # 삭제할 아티스트 조회
        artist.delete()  # 아티스트 삭제
        return Response(
            {"message": "개별 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )  # 삭제 완료 메시지와 204 NO CONTENT 상태 반환


class ArtistGroupListView(APIView):

    # def get_permissions(self):
    #
    #     if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
    #         return [IsAuthenticated()]
    #     return [IsAdminUser()]

    def get(self, request):
        artist_groups = ArtistGroup.objects.all()  # 전체 그룹 아티스트 조회
        serializer = ArtistGroupSerializer(artist_groups, many=True)  # 데이터를 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 200 OK 상태와 함께 데이터를 반환

    def post(self, request):
        serializer = ArtistGroupSerializer(data=request.data)  # 입력된 데이터를 직렬화하여 검증 준비
        if serializer.is_valid():  # 데이터 유효성 검사
            serializer.save()  # 저장
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )  # 생성된 데이터를 201 CREATED 상태와 함께 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환


class ArtistGroupDetailView(APIView):

    # def get_permissions(self):
    #     if self.request.method == "GET":  # method가 get이면 인증된 사용자만 접근 가능하게 권한 수정
    #         return [IsAuthenticated()]
    #     return [IsAdminUser()]

    def get(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 조회할 그룹 아티스트 조회
        serializer = ArtistGroupSerializer(artist_group)  # 데이터를 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 200 OK 상태와 함께 데이터를 반환

    def patch(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 수정할 그룹 아티스트 조회
        serializer = ArtistGroupSerializer(artist_group, data=request.data, partial=True)  # 부분 업데이트를 위한 직렬화
        if serializer.is_valid():  # 유효성 검사
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터를 200 OK 상태와 함께 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 400 BAD REQUEST 반환

    def delete(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 삭제할 그룹 아티스트 조회
        artist_group.delete()  # 그룹 삭제
        return Response(
            {"message": "그룹 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )  # 삭제 완료 메시지와 204 NO CONTENT 상태 반환
