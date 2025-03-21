from django.core.exceptions import ValidationError  # 커스텀 검증 에러를 위해 import
from django.db import models  # Django의 ORM 모델을 사용하기 위한 import

from app.accounts.models import User  # 사용자 모델 import
from app.artists.models import Artist, ArtistGroup  # 아티스트와 아티스트 그룹 모델 import
from app.common.models import BaseModel  # 공통 필드(생성일자, 수정일자 등)를 포함하는 BaseModel import
from app.schedule.models import Schedule  # 스케줄 모델 import


# 광고 정보를 저장하는 모델 (Advertisement)
class Advertisement(BaseModel):
    advertisement_type = models.CharField("광고 타입", max_length=50, null=True)  # 광고 종류를 저장하는 문자 필드
    status = models.BooleanField("광고 상태", null=True, default=False)  # 광고 활성 여부, 기본값은 False
    sent_at = models.DateTimeField("광고 전송시간", null=True)  # 광고가 전송된 시각을 저장하는 필드
    image_url = models.CharField("이미지 URL", max_length=255, null=True)  # 광고 이미지의 URL을 저장
    link_url = models.CharField("링크 URL", max_length=255, null=True)  # 광고 클릭 시 이동할 링크 URL을 저장
    start_date = models.DateTimeField("시작일", null=True)  # 광고 시작일
    end_date = models.DateTimeField("종료일", null=True)  # 광고 종료일

    class Meta:
        db_table = "advertisement"  # 실제 데이터베이스 테이블명 지정
        verbose_name = "광고"  # 관리자 페이지에서 사용할 단수 명칭
        verbose_name_plural = "광고 목록"  # 관리자 페이지에서 사용할 복수 명칭

    def __str__(self):
        return f"{self.advertisement_type} - {self.status}"  # 객체 문자열 표현


# 사용자가 좋아요를 누른 내역을 저장하는 모델 (Likes)
class Likes(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # 사용자가 삭제되면 관련 좋아요도 함께 삭제됨
        verbose_name="사용자",
        db_column="user_id",
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,  # 아티스트가 삭제되면 해당 좋아요도 삭제됨
        db_column="artist_id",
        verbose_name="아티스트",
        null=True,  # 아티스트가 없을 수도 있음
        blank=True,
    )
    artist_group = models.ForeignKey(
        ArtistGroup,
        on_delete=models.CASCADE,  # 아티스트 그룹이 삭제되면 해당 좋아요도 삭제됨
        db_column="artist_group_id",
        verbose_name="아티스트 그룹",
        null=True,  # 아티스트 그룹이 없을 수도 있음
        blank=True,
    )

    class Meta:
        db_table = "likes"  # 데이터베이스 테이블명 지정
        verbose_name = "좋아요"  # 관리자 페이지 단수 명칭
        verbose_name_plural = "좋아요 목록"  # 관리자 페이지 복수 명칭

    def clean(self):
        # 아티스트와 아티스트 그룹 중 하나는 반드시 있어야 함
        if not self.artist and not self.artist_group:
            raise ValidationError("아티스트 또는 아티스트 그룹 중 하나는 반드시 필요합니다.")

    def __str__(self):
        artist_str = str(self.artist) if self.artist else "No Artist"  # 아티스트 정보 문자열화
        group_str = str(self.artist_group) if self.artist_group else "No Group"  # 아티스트 그룹 정보 문자열화
        return f"{self.user} - {artist_str} - {group_str}"  # 전체 정보 문자열 표현


# 사용자가 즐겨찾기에 등록한 스케줄 정보를 저장하는 모델 (Favorites)
class Favorites(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # 사용자가 삭제되면 관련 즐겨찾기도 삭제됨
        db_column="user_id",
        verbose_name="사용자",
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,  # 스케줄이 삭제되면 해당 즐겨찾기도 삭제됨
        db_column="schedule_id",
        verbose_name="일정",
    )

    class Meta:
        db_table = "favorites"  # 데이터베이스 테이블명 지정
        verbose_name = "즐겨찾기"  # 관리자 페이지 단수 명칭
        verbose_name_plural = "즐겨찾기 목록"  # 관리자 페이지 복수 명칭

    def __str__(self):
        return f"{self.user} - {self.schedule}"  # 객체의 문자열 표현


# 알림 정보를 저장하는 모델 (Notifications)
class Notifications(BaseModel):
    is_active = models.BooleanField("알림 활성 여부", null=True, default=False)  # 알림의 읽음/활성 상태를 저장
    likes = models.ForeignKey(
        Likes,
        on_delete=models.SET_NULL,  # 좋아요가 삭제되더라도 알림 기록은 남도록 설정
        db_column="likes_id",
        verbose_name="좋아요",
        null=True,
        blank=True,
    )
    favorites = models.ForeignKey(
        Favorites,
        on_delete=models.SET_NULL,  # 즐겨찾기가 삭제되더라도 알림 기록은 남도록 설정
        db_column="favorites_id",
        verbose_name="즐겨찾기",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "notifications"  # 데이터베이스 테이블명 지정
        verbose_name = "알림"  # 관리자 페이지 단수 명칭
        verbose_name_plural = "알림 목록"  # 관리자 페이지 복수 명칭

    def __str__(self):
        likes_str = self.likes.__str__() if self.likes else "No Likes"  # 좋아요 관련 정보 문자열화
        favorites_str = self.favorites.__str__() if self.favorites else "No Favorites"  # 즐겨찾기 관련 정보 문자열화
        return f"{self.is_active} - {likes_str} - {favorites_str}"  # 전체 알림 정보 문자열 표현