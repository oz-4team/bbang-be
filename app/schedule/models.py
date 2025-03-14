from django.db import models

from app.artists.models import Artist, ArtistGroup
from app.accounts.models import User
from app.common.models import BaseModel

# Create your models here.


class ScheduleImage(BaseModel):
    image_name = models.CharField("이미지 이름", max_length=255, null=True, blank=True)
    image_url = models.CharField("이미지 URL", max_length=255, null=True, blank=True)
    image_type = models.CharField("이미지 타입", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "스케줄 이미지"
        verbose_name_plural = "스케줄 이미지 목록"

    def __str__(self):
        return self.image_name if self.image_name else "Unnamed Image"


class Map(BaseModel):
    map_name = models.CharField("지도 이름", max_length=50, null=True, blank=True)
    map_address = models.CharField("주소", max_length=100, null=True, blank=True)
    latitude = models.DecimalField("위도", max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField("경도", max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return self.map_name if self.map_name else "Unnamed Map"


class Schedule(BaseModel):
    is_active = models.BooleanField("활성화 상태", default=True)
    title = models.CharField("제목", max_length=50)
    description = models.TextField("설명", null=True, blank=True)
    start_date = models.DateTimeField("시작 날짜")
    end_date = models.DateTimeField("종료 날짜")
    location = models.CharField("장소", max_length=100, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True, blank=True)
    artist_group = models.ForeignKey(ArtistGroup, on_delete=models.CASCADE)
    image = models.ForeignKey(ScheduleImage, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "일정"
        verbose_name_plural = "일정 목록"

    def __str__(self):
        return self.title
