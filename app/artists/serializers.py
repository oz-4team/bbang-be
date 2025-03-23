from drf_extra_fields.fields import Base64ImageField  # Base64 인코딩 이미지를 처리하기 위한 필드
from rest_framework import serializers

from app.artists.models import Artist, ArtistGroup


class ArtistGroupSerializer(serializers.ModelSerializer):
    # 그룹 이미지(image_url)를 Base64 형식의 데이터를 받을 수 있도록 정의
    image_url = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ArtistGroup
        fields = "__all__"


class ArtistSerializer(serializers.ModelSerializer):
    artist_group = ArtistGroupSerializer(read_only=True)
    artist_group_id = serializers.PrimaryKeyRelatedField(
        queryset=ArtistGroup.objects.all(),
        source="artist_group",
        write_only=True,
        required=False,
        allow_null=True,
    )
    # 아티스트 이미지(image_url)를 Base64 데이터를 받을 수 있도록 정의
    image_url = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Artist
        fields = "__all__"
