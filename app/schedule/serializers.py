from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from app.artists.models import Artist, ArtistGroup
from app.artists.serializers import ArtistGroupSerializer, ArtistSerializer
from app.schedule.models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    # base64 인코딩 데이터를 받아 S3 등 스토리지에 저장할 수 있도록 처리
    image_url = Base64ImageField(required=False, allow_null=True)

    # 조회 시: artist 필드는 nested serializer로 자세한 정보를 반환
    artist = ArtistSerializer(read_only=True)  # 읽기 전용 아티스트 정보
    # 쓰기 시: artist_id 필드를 통해 아티스트를 설정할 수 있음
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),  # 아티스트 쿼리셋 지정
        source="artist",  # 내부적으로 artist 필드에 할당됨
        write_only=True,  # 쓰기 전용 필드로 설정
        required=False,  # 선택적으로 입력
        allow_null=True,  # 값이 없으면 null 허용
    )

    # 조회 시: artist_group 필드는 nested serializer로 상세 정보를 반환
    artist_group = ArtistGroupSerializer(read_only=True)  # 읽기 전용 그룹 정보
    # 쓰기 시: artist_group_id 필드를 통해 아티스트 그룹을 설정할 수 있음
    artist_group_id = serializers.PrimaryKeyRelatedField(
        queryset=ArtistGroup.objects.all(),  # 아티스트 그룹 쿼리셋 지정
        source="artist_group",  # 내부적으로 artist_group 필드에 할당됨
        write_only=True,  # 쓰기 전용 필드로 설정
        required=False,  # 선택적으로 입력
        allow_null=True,  # 값이 없으면 null 허용
    )

    class Meta:
        model = Schedule  # Schedule 모델과 연결
        fields = [
            "id",
            "is_active",
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "latitude",
            "longitude",
            "user",
            "artist",
            "artist_id",
            "artist_group",
            "artist_group_id",
            "image_url",
        ]
        read_only_fields = ["user"]  # 사용자 필드는 읽기 전용으로 처리

    def create(self, validated_data):
        return super().create(validated_data)
