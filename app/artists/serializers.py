from drf_extra_fields.fields import Base64ImageField  # Base64 인코딩 이미지를 처리하기 위한 필드
from rest_framework import serializers

from app.artists.models import Artist, ArtistGroup
from app.content.models import Likes


class ArtistSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()  # 좋아요 여부
    artist_group_id = serializers.PrimaryKeyRelatedField(
        queryset=ArtistGroup.objects.all(),
        source="artist_group",
        write_only=True,
        required=False,
        allow_null=True,
    )
    group_name = serializers.CharField(source="artist_group.artist_group", read_only=True)  # 실제 그룹 필드명
    # 아티스트 이미지(image_url)를 Base64 데이터를 받을 수 있도록 정의
    image_url = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Artist
        fields = "__all__"

    def get_is_liked(self, obj):
        """현재 user가 이 아티스트를 좋아요했는지 여부"""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        return Likes.objects.filter(user=user, artist=obj).exists()


class ArtistGroupSerializer(serializers.ModelSerializer):
    members = ArtistSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()  # 좋아요 여부
    # 그룹 이미지(image_url)를 Base64 형식의 데이터를 받을 수 있도록 정의
    image_url = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ArtistGroup
        fields = "__all__"

    def get_is_liked(self, obj):
        """현재 user가 이 아티스트그룹을 좋아요했는지 여부"""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Likes.objects.filter(user=request.user, artist_group=obj).exists()


class ArtistGroupDetailSerializer(serializers.ModelSerializer):
    # ArtistGroup 모델의 related_name="members"로 연결된 Artist 목록
    members = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = ArtistGroup
        fields = (
            "id",
            "artist_group",
            "artist_agency",
            "group_insta",
            "group_fandom",
            "debut_date",
            "image_url",
            "members",
        )

    def get_is_liked(self, obj):
        """현재 user가 이 아티스트그룹을 좋아요했는지 여부"""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Likes.objects.filter(user=request.user, artist_group=obj).exists()
