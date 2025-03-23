from django.db import models

from app.common.models import BaseModel


class ArtistGroup(BaseModel):
    artist_group = models.CharField("아티스트 그룹", max_length=30, null=True, blank=True)
    artist_agency = models.CharField("소속사", max_length=30, null=True, blank=True)
    group_insta = models.CharField("인스타그램", max_length=30, null=True, blank=True)
    image_url = models.ImageField("그룹 이미지", upload_to="artist_groups/", null=True, blank=True)
    # image -> image_url 로 변경

    class Meta:
        verbose_name = "아티스트 그룹"
        verbose_name_plural = "아티스트 그룹 목록"

    def __str__(self):
        return self.artist_group


class Artist(BaseModel):
    artist_name = models.CharField("이름", max_length=30, default="Unknown")
    artist_group = models.ForeignKey(ArtistGroup, on_delete=models.CASCADE, null=True, blank=True)
    artist_agency = models.CharField("소속사", max_length=30, null=True, blank=True)
    artist_insta = models.CharField("인스타그램", max_length=30, null=True, blank=True)
    image_url = models.ImageField("아티스트 이미지", upload_to="artists/", null=True, blank=True)
    # image -> image_url 로 변경

    class Meta:
        verbose_name = "아티스트"
        verbose_name_plural = "아티스트 목록"

    def __str__(self):
        return self.artist_name
