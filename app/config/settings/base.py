"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_extensions",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "app.accounts",
    "app.artists",
    "app.common",
    "app.schedule",
    "app.content",
    "app",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

APPEND_SLASH = True

ROOT_URLCONF = "config.urls.dev"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
        "OPTIONS": {
            "sslmode": "require",  # SSL 적용 (RDS에서 필요할 수 있음)
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "accounts.user"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ko-KR"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
}

SIMPLE_JWT = {  # 심플 JWT 세팅
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # 액세스토큰 시간
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # 리프레시토큰 시간
    "ROTATE_REFRESH_TOKENS": False,
    # refresh 토큰 재발급 여부 설정  -> True 설정시 refrsh token 제출 시 새 엑세스 토큰 + 새 리프레쉬 토큰 반환
    "BLACKLIST_AFTER_ROTATION": True,  # 토큰 사용 후 블랙리스트 적용
    # 사용된 리프레쉬 토큰 블랙리스트 추가
    "AUTH_HEADER_TYPES": ("Bearer",),  # 인증 헤더에 사용할 토큰 타입 지정
}

# 이메일 백엔드 (개발 콘솔용) *수정 필요

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # SMTP 백엔드 사용
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL")
# os.environ.get -> 환경변수에서 값을 우선 가져온 후 없으면 뒤에 있는 값
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")  # 네이버 아이디@naver.com
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD"
)  # 네이버 비밀번호  -> 깃허브 시크릿 EMAIL_HOST_PASSWORD / 비밀번호 세팅
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")  # 기본 발신자 이메일 주소
SITE_URL = os.environ.get("SITE_URL")  # 나중에 도메인으로 변경

# 구글 OAuth2 관련 설정
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

# 카카오 OAuth2 관련 설정
KAKAO_CLIENT_ID = os.environ.get("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.environ.get("KAKAO_REDIRECT_URI")

# 네이버 OAuth2 관련 설정
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.environ.get("NAVER_REDIRECT_URI")

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# Static, Media URL 수정
STATIC_URL = f'https://{os.environ.get("S3_STORAGE_BUCKET_NAME", "bbang")}.s3.amazonaws.com/static/'
MEDIA_URL = f'https://{os.environ.get("S3_STORAGE_BUCKET_NAME", "bbang")}.s3.amazonaws.com/media/'


# STORAGES 작성
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.environ.get("S3_ACCESS_KEY", ""),
            "secret_key": os.environ.get("S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": os.environ.get("S3_STORAGE_BUCKET_NAME", ""),
            "region_name": os.environ.get("S3_REGION_NAME", ""),
            "location": "media",
            "default_acl": "public-read",
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.environ.get("S3_ACCESS_KEY", ""),
            "secret_key": os.environ.get("S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": os.environ.get("S3_STORAGE_BUCKET_NAME", ""),
            "region_name": os.environ.get("S3_REGION_NAME", ""),
            "custom_domain": f'{os.environ.get("S3_STORAGE_BUCKET_NAME", "")}.s3.amazonaws.com',
            "location": "static",
            "default_acl": "public-read",
        },
    },
}
