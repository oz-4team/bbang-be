from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.artists.models import Artist, ArtistGroup
from app.artists.serializers import ArtistSerializer, ArtistGroupSerializer


class ArtistAndGroupListView(APIView):  # 개별 아티스트와 그룹 아티스트를 동시에 조회
    def get(self, request):
        artists = Artist.objects.all()  # 개별 아티스트 조회
        artist_groups = ArtistGroup.objects.all()  # 그룹 아티스트 조회
        artist_serializer = ArtistSerializer(artists, many=True) # 직렬화
        artist_group_serializer = ArtistGroupSerializer(artist_groups, many=True) # 직렬화
        return Response({
            "artists": artist_serializer.data,  # 반환
            "artist_groups": artist_group_serializer.data,
        }, status=status.HTTP_200_OK) # 상태코드


class ArtistListView(APIView):  # 개별 아티스트 전체조회 및 생성

    def get(self, request):   # 전체 아티스트 개별 조회
        artists = Artist.objects.all()  # 아티스트 전체 조회
        serializer = ArtistSerializer(artists, many=True)  #직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 반환, 상태코드

    def post(self, request):  # 개별 아티스트 생성
        data = request.data.copy()  # copy해 mutable한 복사본으로 생성
        # 클라이언트에서 artist_group_id가 전달되면 그룹 할당  # artist_group_id가 있으면 처리
        artist_group_id = data.get("artist_group_id")  # mutable copy에서 artist_group_id 추출
        if artist_group_id:  # 아티스트 그룹 아이디가 있으면
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 존재하는 그룹 조회
            data["artist_group"] = artist_group.id  # artist_group 필드에 그룹 ID 할당
        else:
            data["artist_group"] = None  # 없으면 None으로 처리

        serializer = ArtistSerializer(data=data)  # 수정된 data로 직렬화 객체 생성
        if serializer.is_valid():  # 유효성 검사
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # 저장된 데이터 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 오류 발생 시 반환

class ArtistDetailView(APIView):  # 개별 아티스트 상세조회, 수정, 삭제

    def get(self, request, artist_id):  # 조회
        artist = get_object_or_404(Artist, id=artist_id)   # 아티스트 아이디로 조회 없으면 404
        serializer = ArtistSerializer(artist)   # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK) # 직렬화 데이터, 상태코드

    def patch(self, request, artist_id):   # 수정
        artist = get_object_or_404(Artist, id=artist_id) # 아티스트 조회 없으면 404
        artist_group_id = request.data.get("artist_group_id")   # 아티스트 그룹 아이디 가져오기
        if artist_group_id is not None:  # 아티스트 그룹 아이디가 None값이 아니면
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id) # 아티스트 그룹 아이디로 조회 없으면 404
            request.data["artist_group"] = artist_group.id  # 아티스트 그룹 = 아티스트 그룹 아이디
        else:
            request.data["artist_group"] = None  # 없으면 아티스트 그룹 아이디가 None값으로 변경

        serializer = ArtistSerializer(artist, data=request.data, partial=True)  #직렬화
        if serializer.is_valid():  # 유효하면
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_200_OK) # 반환, 상태코드
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러시 메시지, 상태코드반환

    def delete(self, request, artist_id):   # 삭제
        artist = get_object_or_404(Artist, id=artist_id)  # 아티스트 아이로 조회 없으면 404
        artist.delete()  # 아티스트 삭제
        return Response({"message": "개별 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)  # 메시지 상태코드


class ArtistGroupListView(APIView):

    def get(self, request):  # 그룹 전체조회
        artist_groups = ArtistGroup.objects.all()  # 아티스트 그룹 전체 조회
        serializer = ArtistGroupSerializer(artist_groups, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)  # 반환 상태코드

    def post(self, request):  # 그룹 생성
        serializer = ArtistGroupSerializer(data=request.data)  # 받은 데이터 직렬화
        if serializer.is_valid(): # 유효하면
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # 반환, 상태코드
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러반환 , 상태코드


class ArtistGroupDetailView(APIView):
    def get(self, request, artist_group_id):  # 그룹 상세조회
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id) # 조회 없으면 404
        serializer = ArtistGroupSerializer(artist_group)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK) # 반환 , 상태코드

    def patch(self, request, artist_group_id):  # 그룹 수정
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)  # 그룹 조회 없으면 404
        serializer = ArtistGroupSerializer(artist_group, data=request.data, partial=True)  # 직렬화
        if serializer.is_valid():  # 유효하면
            serializer.save() # 저장
            return Response(serializer.data, status=status.HTTP_200_OK) # 반환, 상태코드
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 에러메세지, 상태코드 반환

    def delete(self, request, artist_group_id):   # 그룹 삭제
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id) # 아티스트 그룹 조회
        artist_group.delete()  # 그룹 삭제
        return Response({"message": "그룹 아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT) # 메시지 상태코드