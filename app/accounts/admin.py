from django.contrib import admin  # Django의 관리자(admin) 관련 모듈 import

from app.accounts.models import User


# CustomUser 모델에 대한 관리자 설정
class CustomUserAdmin(admin.ModelAdmin):  # type: ignore
    # 페이지에 표시할 필드들 설정
    list_display = ("email", "nickname")
    # 하이퍼링크 설정
    list_display_links = ["email", "nickname"]
    # 닉네임으로 검색가능
    search_fields = ("nickname", "email")
    # 활성여부, 관리자 여부로 필터링가능
    list_filter = ["is_staff", "is_active"]

    # 관리자 상세 페이지에서 보여줄 필드 구분(Fieldsets) 설정
    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "email",
                ),
            },
        ),
        (
            "개인 정보",
            {
                "fields": ("nickname",),
            },
        ),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    readonly_fields = (
        "is_superuser",
    )  # 관리자가 읽을수 있게 설정
    # 사용자 생성 시 추가 필드 설정
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),  # CSS 클래스 지정 (wide: 넓은 폼)
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "nickname",
                ),  # 생성 시 필요한 필드들
            },
        ),
    )


# 관리자 사이트에 모델과 관리자 설정 등록
admin.site.register(User, CustomUserAdmin)
