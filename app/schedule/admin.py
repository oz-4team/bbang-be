from django.contrib import admin

from app.schedule.models import Schedule  # Schedule 모델 import


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "start_date",
        "end_date",
        "location",
        "artist",
        "artist_group",
        "is_active",
    )  # 리스트에서 보여줄 필드 설정
    list_filter = ("is_active", "start_date", "artist", "artist_group")  # 필터 옵션
    search_fields = ("title", "location", "artist__artist_name", "artist_group__group_name")  # 검색 필드
