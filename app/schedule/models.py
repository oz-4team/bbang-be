from django.db import models
from django.utils import timezone

from app.accounts.models import User
from app.artists.models import Artist, ArtistGroup
from app.common.models import BaseModel

# Create your models here.


class Schedule(BaseModel):
    is_active = models.BooleanField("활성화 상태", default=True)
    title = models.CharField("제목", max_length=50)
    description = models.TextField("설명", null=True, blank=True)
    start_date = models.DateTimeField("시작 날짜", default=timezone.now)
    end_date = models.DateTimeField("종료 날짜", default=timezone.now)
    location = models.CharField("장소", max_length=100, null=True, blank=True)
    latitude = models.DecimalField(
        "위도", max_digits=10, decimal_places=7, null=True, blank=True
    )  # 최대 10자리 숫자 중 소수점 이하 7자리 허용
    longitude = models.DecimalField(
        "경도", max_digits=10, decimal_places=7, null=True, blank=True
    )  # 최대 10자리 숫자 중 소수점 이하 7자리 허용
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    artist_group = models.ForeignKey(ArtistGroup, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.ImageField("일정 이미지", upload_to="schedule/", null=True, blank=True)

    class Meta:
        verbose_name = "일정"
        verbose_name_plural = "일정 목록"

    def __str__(self):
        return self.title
