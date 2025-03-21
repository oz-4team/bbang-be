from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.artists.models import Artist, ArtistGroup
from app.artists.serializers import ArtistGroupSerializer, ArtistSerializer


class ArtistAndGroupListView(APIView):
    """
    아티스트와 아티스트 그룹 전체 데이터를 조회하는 API
    """

    def get(self, request):
        artists = Artist.objects.all()
        artist_groups = ArtistGroup.objects.all()

        artist_serializer = ArtistSerializer(artists, many=True)
        artist_group_serializer = ArtistGroupSerializer(artist_groups, many=True)

        return Response(
            {
                "artists": artist_serializer.data,
                "artist_groups": artist_group_serializer.data,
            }
        )


class ArtistView(APIView):
    """
    아티스트 목록 조회 및 생성
    """

    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

    def post(self, request):
        artist_group_id = request.data.get("artist_group_id", None)
        if artist_group_id:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
            request.data["artist_group"] = artist_group.id
        else:
            request.data["artist_group"] = None  # 그룹 없이도 생성 가능

        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistDetailView(APIView):
    """
    특정 아티스트 조회, 수정, 삭제
    """

    def get(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        serializer = ArtistSerializer(artist)
        return Response(serializer.data)

    def patch(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        artist_group_id = request.data.get("artist_group_id", None)

        if artist_group_id:
            artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
            request.data["artist_group"] = artist_group.id
        else:
            request.data["artist_group"] = None  # 그룹을 없앨 수도 있음

        serializer = ArtistSerializer(artist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, artist_id):
        artist = get_object_or_404(Artist, id=artist_id)
        artist.delete()
        return Response({"message": "아티스트가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class ArtistGroupView(APIView):
    """
    아티스트 그룹 목록 조회 및 생성
    """

    def get(self, request):
        artist_groups = ArtistGroup.objects.all()
        serializer = ArtistGroupSerializer(artist_groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArtistGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistGroupDetailView(APIView):
    """
    특정 아티스트 그룹 조회, 수정, 삭제
    """

    def get(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
        serializer = ArtistGroupSerializer(artist_group)
        return Response(serializer.data)

    def patch(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
        serializer = ArtistGroupSerializer(artist_group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, artist_group_id):
        artist_group = get_object_or_404(ArtistGroup, id=artist_group_id)
        artist_group.delete()
        return Response({"message": "아티스트 그룹이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

