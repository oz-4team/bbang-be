from rest_framework import serializers

from app.artists.models import Artist, ArtistGroup


class ArtistGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistGroup
        fields = "__all__"


class ArtistSerializer(serializers.ModelSerializer):
    artist_group = ArtistGroupSerializer(read_only=True)  # 조회 시 그룹 정보 포함
    artist_group_id = serializers.PrimaryKeyRelatedField(
        queryset=ArtistGroup.objects.all(),
        source="artist_group",
        write_only=True,
        required=False,
        allow_null=True,  # 그룹이 없을 수도 있음
    )

    class Meta:
        model = Artist
        fields = "__all__"
