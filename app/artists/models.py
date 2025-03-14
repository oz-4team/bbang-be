from django.db import models

from app.common.models import BaseModel


# Create your models here.
class ArtistImage(BaseModel):
    image_name = models.CharField("이미지 이름", max_length=255, null=True, blank=True)
    image_url = models.CharField("이미지 URL", max_length=255, null=True, blank=True)
    image_type = models.CharField("이미지 타입", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "아티스트 이미지"
        verbose_name_plural = "아티스트 이미지 목록"

    def __str__(self):
        return self.image_name if self.image_name else "Unnamed Image"


class ArtistGroupImage(BaseModel):
    image_name = models.CharField("이미지 이름", max_length=255, null=True, blank=True)
    image_url = models.CharField("이미지 URL", max_length=255, null=True, blank=True)
    image_type = models.CharField("이미지 타입", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "아티스트 그룹 이미지"
        verbose_name_plural = "아티스트 그룹 이미지 목록"

    def __str__(self):
        return self.image_name if self.image_name else "Unnamed Image"


class ArtistGroup(BaseModel):
    artist_group = models.CharField("아티스트 그룹", max_length=30)
    artist_agency = models.CharField("소속사", max_length=30)
    group_insta = models.CharField("인스타그램", max_length=30, null=True, blank=True)
    image = models.ForeignKey(ArtistGroupImage, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "아티스트 그룹"
        verbose_name_plural = "아티스트 그룹 목록"

    def __str__(self):
        return self.artist_group


class Artist(BaseModel):
    artist_name = models.CharField("이름", max_length=30)
    artist_group = models.ForeignKey(ArtistGroup, on_delete=models.CASCADE)
    artist_agency = models.CharField("소속사", max_length=30)
    artist_insta = models.CharField("인스타그램", max_length=30, null=True, blank=True)
    image = models.ForeignKey(ArtistImage, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "아티스트"
        verbose_name_plural = "아티스트 목록"

    def __str__(self):
        return self.artist_name
