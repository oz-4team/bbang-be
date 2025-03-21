from django.contrib import admin
from .models import ArtistGroup, Artist

class ArtistGroupAdmin(admin.ModelAdmin):
    list_display = ('artist_group', 'artist_agency', 'group_insta')
    search_fields = ('artist_group', 'artist_agency', 'group_insta')
    list_filter = ('artist_agency',)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('artist_name', 'artist_group', 'artist_agency', 'artist_insta')
    search_fields = ('artist_name', 'artist_group__artist_group', 'artist_agency', 'artist_insta')
    list_filter = ('artist_agency', 'artist_group')
    raw_id_fields = ('artist_group',)  # ForeignKey 필드에서 편리한 검색을 위해 raw_id_fields 사용

admin.site.register(ArtistGroup, ArtistGroupAdmin)
admin.site.register(Artist, ArtistAdmin)
