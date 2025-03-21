# app/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from app.artists.models import Artist, ArtistGroup
from app.schedule.models import Schedule

class MyAdminSite(AdminSite):
    site_header = "Bbang Admin"
    site_title = "Bbang Admin Portal"
    index_title = "관리자 페이지"

    def has_permission(self, request):
        # 오직 superuser만 admin 페이지에 접근할 수 있도록 설정
        return request.user.is_active and request.user.is_superuser

# 인스턴스 생성
admin_site = MyAdminSite(name='myadmin')

# 기존 model registration을 custom admin site에 등록
@admin.register(Artist, site=admin_site)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('artist_name', 'artist_group', 'artist_agency', 'artist_insta')

@admin.register(ArtistGroup, site=admin_site)
class ArtistGroupAdmin(admin.ModelAdmin):
    list_display = ('artist_group', 'artist_agency', 'group_insta')

@admin.register(Schedule, site=admin_site)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location')

# 그리고 기존 admin.site.unregister() 또는 admin.site.register()를 사용하지 않도록 주의