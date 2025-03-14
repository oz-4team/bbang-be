from django.db import models

from app.common.models import BaseModel


class UserImage(BaseModel):
    id = models.IntegerField(primary_key=True)  # 사용자 이미지의 식별자
    image_name = models.CharField("이미지 이름", max_length=255, null=True)  # 이름
    image_url = models.CharField("이미지 url", max_length=255, null=True)  # URL
    image_type = models.CharField("이미지 타입", max_length=255, null=True)  # 타입

    class Meta:
        verbose_name = "유저 이미지"
        verbose_name_plural = "유저 이미지목록"

    def __str__(self):
        return f"{self.image_name}"


class User(BaseModel):
    id = models.IntegerField(primary_key=True)  # 사용자의 식별자
    email = models.CharField("이메일", max_length=100, null=True, unique=True)  # 이메일
    password = models.CharField("비밀번호", max_length=30, null=True)  # 비밀번호
    nickname = models.CharField("닉네임", max_length=30, null=True)  # 닉네임
    is_active = models.BooleanField("활성상태", null=True)  # 활성화 상태
    is_staff = models.BooleanField("스태프", null=True)  # 스태프 권한
    gender = models.CharField("성별", max_length=1, null=True)  # 성별 (M, F)
    age = models.IntegerField("나이", null=True)  # 나이
    social_provider = models.CharField("소설 제공자", max_length=20, null=True)  # 소셜 제공자
    social_id = models.CharField("소설 아이디", max_length=50, null=True)  # 소셜 로그인 식별자
    user_image = models.ForeignKey(
        UserImage, on_delete=models.SET_DEFAULT, default=1  # 이미지 삭제되면 Default 값 설정
    )

    class Meta:
        verbose_name = "유저"
        verbose_name_plural = "유저 목록"

    def __str__(self):
        return f"{self.nickname}"
