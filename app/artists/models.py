from django.db import models

from app.accounts.models import User
from app.common.models import BaseModel


class ArtistGroup(BaseModel):
    artist_group = models.CharField("아티스트 그룹", max_length=30, null=True, blank=True)
    artist_agency = models.CharField("소속사", max_length=30, null=True, blank=True)
    group_insta = models.CharField("인스타그램", max_length=100, null=True, blank=True)
    group_fandom = models.CharField("아티스트그룹팬덤", max_length=10, null=True, blank=True)
    debut_date = models.DateField("데뷔 날짜", null=True, blank=True)
    image_url = models.ImageField("그룹 이미지", upload_to="artist_groups/", null=True, blank=True)
    # image -> image_url 로 변경
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="created_groups")

    class Meta:
        verbose_name = "아티스트 그룹"
        verbose_name_plural = "아티스트 그룹 목록"

    def __str__(self):
        return self.artist_group or "No Name"


class Artist(BaseModel):
    artist_name = models.CharField("이름", max_length=30, default="Unknown")
    artist_group = models.ForeignKey(
        ArtistGroup, on_delete=models.CASCADE, null=True, blank=True, related_name="members"
    )
    solomembers = models.BooleanField("솔로활동", null=True, blank=True, default=False)
    artist_agency = models.CharField("소속사", max_length=30, null=True, blank=True)
    artist_insta = models.CharField("인스타그램", max_length=100, null=True, blank=True)
    artist_fandom = models.CharField("아티스트팬덤", max_length=10, null=True, blank=True)
    debut_date = models.DateField("데뷔 날짜", null=True, blank=True)
    image_url = models.ImageField("아티스트 이미지", upload_to="artists/", null=True, blank=True)
    # image -> image_url 로 변경
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="created_artists"
    )

    class Meta:
        verbose_name = "아티스트"
        verbose_name_plural = "아티스트 목록"

    def __str__(self):
        return self.artist_name or "No Name"
