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
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", verbose_name="사용자")
    # 좋아요 대상이 될 수 있는 아티스트 (optional)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, db_column="artist_id", verbose_name="아티스트", null=True, blank=True
    )
    # 좋아요 대상이 될 수 있는 아티스트 그룹 (optional)
    artist_group = models.ForeignKey(
        ArtistGroup,
        on_delete=models.CASCADE,
        db_column="artist_groups_id",
        verbose_name="아티스트 그룹",
        null=True,
        blank=True,
    )

    def clean(self):
        """
        좋아요는 아티스트 OR 아티스트 그룹 중 정확히 하나가 지정되어야 합니다.
        """
        if (self.artist is None and self.artist_group is None) or (
            self.artist is not None and self.artist_group is not None
        ):
            raise ValidationError("좋아요는 아티스트 또는 아티스트 그룹 중 하나만 지정할 수 있습니다.")

    class Meta:
        db_table = "likes"
        verbose_name = "좋아요"
        verbose_name_plural = "좋아요 목록"
        constraints = [
            # 각 사용자-아티스트 조합은 유일해야 합니다.
            models.UniqueConstraint(
                fields=["user", "artist"], condition=models.Q(artist__isnull=False), name="unique_user_artist_like"
            ),
            # 각 사용자-아티스트그룹 조합은 유일해야 합니다.
            models.UniqueConstraint(
                fields=["user", "artist_group"],
                condition=models.Q(artist_group__isnull=False),
                name="unique_user_artistgroup_like",
            ),
        ]

    def __str__(self):
        if self.artist:
            target = f"아티스트: {self.artist}"
        else:
            target = f"아티스트 그룹: {self.artist_group}"
        return f"{self.user} - {target}"

    def clean(self):
        """
        아티스트와 아티스트 그룹 중 적어도 하나는 반드시 선택되어야 합니다.
        """
        from django.core.exceptions import ValidationError

        if not self.artist and not self.artist_group:
            raise ValidationError("좋아요는 아티스트 또는 아티스트 그룹 중 하나를 선택해야 합니다.")

    def __str__(self):
        # __str__은 선택된 값에 따라 표시합니다.
        artist_info = self.artist.__str__() if self.artist else "No Artist"
        group_info = self.artist_group.__str__() if self.artist_group else "No Group"
        return f"{self.user} - {artist_info} - {group_info}"


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
