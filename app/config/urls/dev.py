from django.urls import re_path, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view  # type: ignore
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .base import urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="IDOLSYNC API",
        default_version="v1",
        description="API 문서입니다.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# 기존 경로에 새로운 URL 패턴 추가
urlpatterns = list(urlpatterns)
urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(r"redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
