from django.contrib import admin
from django.utils.html import format_html

from .models import Artist, ArtistGroup


class ArtistGroupAdmin(admin.ModelAdmin):
    list_display = ("artist_group", "artist_agency", "group_insta", "image_preview")
    search_fields = ("artist_group", "artist_agency", "group_insta")
    list_filter = ("artist_agency",)

    def image_preview(self, obj):
        # image_url 필드에 값이 있다면, 미리보기 이미지 HTML을 반환
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image_url.url)
        return "-"

    image_preview.short_description = "그룹 이미지 미리보기"


class ArtistAdmin(admin.ModelAdmin):
    list_display = ("artist_name", "artist_group", "artist_agency", "artist_insta", "image_preview")
    search_fields = ("artist_name", "artist_group__artist_group", "artist_agency", "artist_insta")
    list_filter = ("artist_agency", "artist_group")
    raw_id_fields = ("artist_group",)  # 편리한 FK 검색을 위해

    def image_preview(self, obj):
        # image_url 필드에 값이 있다면, 미리보기 이미지 HTML을 반환
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image_url.url)
        return "-"

    image_preview.short_description = "아티스트 이미지 미리보기"


admin.site.register(ArtistGroup, ArtistGroupAdmin)
admin.site.register(Artist, ArtistAdmin)
