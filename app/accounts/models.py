from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from app.common.models import BaseModel


class UserImage(BaseModel):
    image_name = models.CharField("이미지 이름", max_length=255, null=True)  # 이미지 이름
    image_url = models.CharField("이미지 URL", max_length=255, null=True)  # 이미지 URL
    image_type = models.CharField("이미지 타입", max_length=255, null=True)  # 이미지 파일 타입

    class Meta:
        db_table = "user_image"  # 실제 DB 테이블명
        verbose_name = "유저 이미지"
        verbose_name_plural = "유저 이미지목록"

    def __str__(self):
        return f"{self.image_name or '기본 이미지'}"  # 이미지 이름이 없으면 기본 이미지


# 커스텀 유저 매니저: 커스텀 유저 생성 및 슈퍼유저 생성을 위한 메서드를 정의
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        이메일을 기반으로 일반 유저를 생성하는 메서드입니다.
        """
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱 처리
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None, **extra_fields):  # 각 아티스트의 스태프 계정
        extra_fields.setdefault("is_staff", True)  # 스태프 True
        extra_fields.setdefault("is_superuser", False)  # 슈퍼유저 True

        if extra_fields.get("is_staff") is not True:
            raise ValueError("스태프가 아닙니다.")

        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):  # 웹 관리자 계정
        extra_fields.setdefault("is_staff", True)  # 스태프 True
        extra_fields.setdefault("is_active", True)  # 활성상태 True
        extra_fields.setdefault("is_superuser", True)  # 슈퍼유저 True

        if extra_fields.get("is_staff") is not True:
            raise ValueError("스태프가 아닙니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("총 관리자가 아닙니다.")

        return self.create_user(email, password, **extra_fields)


# user
class User(BaseModel, AbstractBaseUser, PermissionsMixin):  # BaseModel => created_at, updated_at 불러옴
    email = models.EmailField("이메일", max_length=100, unique=True, null=True)  # 유일한 이메일 필드
    nickname = models.CharField("닉네임", max_length=30, null=True)  # 닉네임
    is_active = models.BooleanField("활성 상태", default=False)  # 회원가입 후 이메일 인증 시 True로 업데이트됨
    is_staff = models.BooleanField("스태프 여부", default=False)  # 일반 유저는 False, 아티스트 스태프는 True
    gender = models.CharField("성별", max_length=1, null=True)  # 성별 (예: 'M', 'F')
    age = models.IntegerField("나이", null=True)  # 나이
    social_provider = models.CharField("소셜 제공자", max_length=20, null=True)  # 소셜 로그인 제공자
    social_id = models.CharField("소셜 아이디", max_length=50, null=True)  # 소셜 로그인 식별자
    user_image = models.ForeignKey(
        UserImage,
        on_delete=models.SET_DEFAULT,  # 참조된 이미지가 삭제되면 기본 이미지로 설정
        default=1,  # 기본 이미지의 id 값
        verbose_name="유저 이미지",
        db_column="user_image_key",
        null=True,
    )

    objects = CustomUserManager()  # 커스텀 매니저 지정

    USERNAME_FIELD = "email"  # 로그인 시 사용할 필드는 이메일
    REQUIRED_FIELDS = ["nickname"]  # 추가 필수 항목

    class Meta:
        db_table = "user"  # 실제 DB 테이블명
        verbose_name = "유저"
        verbose_name_plural = "유저 목록"

    def __str__(self):
        # 닉네임이 없으면 이메일을 반환
        return f"{self.nickname or self.email}"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # 인스턴스가 저장될때 save를 오버라이드해 소문자로 변환시킴
        super().save(*args, **kwargs)
