from django.core.exceptions import ValidationError
from django.db import models

from app.accounts.models import User
from app.artists.models import Artist, ArtistGroup
from app.common.models import BaseModel
from app.schedule.models import Schedule


# 광고 모델
class Advertisement(BaseModel):
    advertisement_type = models.CharField("광고 타입", max_length=50, null=True)
    status = models.BooleanField("광고 상태", null=True, default=False)
    sent_at = models.DateTimeField("광고 전송시간", null=True)
    image_url = models.ImageField(
        "광고 이미지",  # 필드 설명: 프로필 이미지
        upload_to="Advertisement_images/",  # 이미지 저장 경로 (AWS S3의 폴더 경로 지정)
        null=True,  # DB에 null 허용
        blank=True,  # 폼에서 빈 값 허용
    )
    link_url = models.CharField("링크 URL", max_length=255, null=True)
    start_date = models.DateTimeField("시작일", null=True)
    end_date = models.DateTimeField("종료일", null=True)

    class Meta:
        db_table = "advertisement"
        verbose_name = "광고"
        verbose_name_plural = "광고 목록"

    def __str__(self):
        return f"{self.advertisement_type} - {self.status}"


# 좋아요 모델
class Likes(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="사용자",
        db_column="user_id",
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        db_column="artist_id",
        verbose_name="아티스트",
        null=True,
        blank=True,
    )
    artist_group = models.ForeignKey(
        ArtistGroup,
        on_delete=models.CASCADE,
        db_column="artist_group_id",
        verbose_name="아티스트 그룹",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "likes"
        verbose_name = "좋아요"
        verbose_name_plural = "좋아요 목록"

    def clean(self):
        # 아티스트 또는 아티스트 그룹 중 하나는 반드시 있어야 함
        if not self.artist and not self.artist_group:
            raise ValidationError("아티스트 또는 아티스트 그룹 중 하나는 반드시 필요합니다.")

    def __str__(self):
        artist_str = str(self.artist) if self.artist else "No Artist"
        group_str = str(self.artist_group) if self.artist_group else "No Group"
        return f"{self.user} - {artist_str} - {group_str}"


# 즐겨찾기 모델
class Favorites(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        verbose_name="사용자",
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        db_column="schedule_id",
        verbose_name="일정",
    )

    class Meta:
        db_table = "favorites"
        verbose_name = "즐겨찾기"
        verbose_name_plural = "즐겨찾기 목록"

    def __str__(self):
        return f"{self.user} - {self.schedule}"


# 알림 모델
class Notifications(BaseModel):
    is_active = models.BooleanField("알림 활성 여부", null=True, default=False)
    likes = models.ForeignKey(
        Likes,
        on_delete=models.SET_NULL,
        db_column="likes_id",
        verbose_name="좋아요",
        null=True,
        blank=True,
    )
    favorites = models.ForeignKey(
        Favorites,
        on_delete=models.SET_NULL,
        db_column="favorites_id",
        verbose_name="즐겨찾기",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "notifications"
        verbose_name = "알림"
        verbose_name_plural = "알림 목록"

    def __str__(self):
        likes_str = self.likes.__str__() if self.likes else "No Likes"
        favorites_str = self.favorites.__str__() if self.favorites else "No Favorites"
        return f"{self.is_active} - {likes_str} - {favorites_str}"


class authority(BaseModel):
    artistName = models.CharField("아티스트(개인, 그룹) 이름", max_length=20)
    artist_agency = models.CharField("소속사", max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="신청 유저")
    phone_number = models.CharField("전화번호", max_length=15)
    image_url = models.ImageField(
        "첨부파일",  # 필드 설명: 첨부파일
        upload_to="authority/",  # 이미지 저장 경로 (AWS S3의 폴더 경로 지정)
        null=True,  # DB에 null 허용
        blank=True,  # 폼에서 빈 값 허용
    )

    class Meta:
        verbose_name = "권한 신청"
        verbose_name_plural = "권한 신청 목록"

    def __str__(self):
        return f"{self.artistName} - {self.artist_agency} - 권한 신청자 = {self.user.email}"
