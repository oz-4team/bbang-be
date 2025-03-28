from django.conf import settings
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .base import urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="API 문서",
        default_version="v1",
        description="API 문서",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="https://seonhm.kr",  # 여기서 URL을 명시적으로 설정
)


# 기존 경로에 새로운 URL 패턴 추가
urlpatterns = list(urlpatterns)
urlpatterns += [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-ui"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
