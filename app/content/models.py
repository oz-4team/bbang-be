from django.core.exceptions import ValidationError
from django.db import models

from app.accounts.models import User
from app.artists.models import Artist, ArtistGroup
from app.common.models import BaseModel
from app.schedule.models import Schedule


# 광고 테이블
class Advertisement(BaseModel):
    advertisement_type = models.CharField("광고 타입", max_length=50, null=True)  # 광고 종류
    status = models.BooleanField("광고 상태", null=True, default=False)  # 상태 (기본 False)
    sent_at = models.DateTimeField("광고 전송시간", null=True)  # 전송 시각
    image_url = models.CharField("이미지 URL", max_length=255, null=True)  # 광고 이미지 URL (저장한 이미지 URL)
    link_url = models.CharField("링크 URL", max_length=255, null=True)  # 링크 URL
    start_date = models.DateTimeField("시작일", null=True)  # 시작 날짜
    end_date = models.DateTimeField("종료일", null=True)  # 종료 날짜

    class Meta:
        db_table = "advertisement"  # 실제 DB 테이블명
        verbose_name = "광고"
        verbose_name_plural = "광고 목록"

    def __str__(self):
        return f"{self.advertisement_type} - {self.status}"


# 좋아요 테이블
class Likes(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="사용자",
        db_column="user_id",
    )
    # 아티스트
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        db_column="artist_id",
        verbose_name="아티스트",
        null=True,
        blank=True,
    )
    # 아티스트 그룹
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
        if not self.artist and not self.artist_group:
            raise ValidationError("아티스트 또는 아티스트 그룹 중 하나는 반드시 필요합니다.")
        # 하나의 아티스트나 아티스트 그룹은 좋아요해야하고 둘다 좋아요도 가능함

    def __str__(self):
        artist_str = str(self.artist) if self.artist else "No Artist"
        group_str = str(self.artist_group) if self.artist_group else "No Group"
        return f"{self.user} - {artist_str} - {group_str}"


# 즐겨찾기 테이블
class Favorites(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", verbose_name="사용자")
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, db_column="schedule_id", verbose_name="일정")

    class Meta:
        db_table = "favorites"
        verbose_name = "즐겨찾기"
        verbose_name_plural = "즐겨찾기 목록"

    def __str__(self):
        return f"{self.user} - {self.schedule}"


# 알림 테이블
class Notifications(BaseModel):
    is_active = models.BooleanField("알림 활성 여부", null=True, default=False)  # 읽음/안읽음 여부
    # 좋아요, 즐겨찾기가 삭제되어도 알림 기록은 남아있도록 on_delete=SET_NULL 사용
    likes = models.ForeignKey(
        Likes, on_delete=models.SET_NULL, db_column="likes_id", verbose_name="좋아요", null=True, blank=True
    )
    favorites = models.ForeignKey(
        Favorites, on_delete=models.SET_NULL, db_column="favorites_id", verbose_name="즐겨찾기", null=True, blank=True
    )

    class Meta:
        db_table = "notifications"
        verbose_name = "알림"
        verbose_name_plural = "알림 목록"

    def __str__(self):
        likes_str = self.likes.__str__() if self.likes else "No Likes"
        favorites_str = self.favorites.__str__() if self.favorites else "No Favorites"
        return f"{self.is_active} - {likes_str} - {favorites_str}"
