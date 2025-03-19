from django.contrib import admin

from app.content.models import Advertisement, Favorites, Likes, Notifications


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    # 관리자 페이지에서 보여줄 필드들
    list_display = ("advertisement_type", "status", "sent_at", "start_date", "end_date")
    search_fields = ("advertisement_type",)
    list_filter = ("status", "start_date", "end_date")


@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    # 좋아요 객체의 사용자, 아티스트, 아티스트 그룹 정보를 표시
    list_display = ("user", "artist", "artist_group")
    search_fields = ("user__email", "artist__artist_name", "artist_group__artist_group")
    list_filter = ("artist", "artist_group")


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    # 즐겨찾기 객체의 사용자와 일정 정보를 표시
    list_display = ("user", "schedule")
    search_fields = ("user__email", "schedule__title")
    list_filter = ("schedule",)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    # 알림 객체의 활성 상태, 좋아요, 즐겨찾기 정보를 표시
    list_display = ("is_active", "likes", "favorites")
    list_filter = ("is_active",)
