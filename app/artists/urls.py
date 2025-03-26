from django.urls import path

from app.artists.views import (
    ArtistAndGroupListView,
    ArtistDetailView,
    ArtistGroupDetailView,
    ArtistGroupListView,
    ArtistListView, StaffArtistAndGroupListView, ArtistGroupMemberAddView, ArtistGroupMemberCreateView,
    ArtistGroupMemberDeleteView,
)

urlpatterns = [
    path("artists-and-groups/", ArtistAndGroupListView.as_view(), name="artist-and-group-list"),
    path("artists/", ArtistListView.as_view(), name="artist-list"),
    path("artists/<int:artist_id>/", ArtistDetailView.as_view(), name="artist-detail"),
    path("artist-groups/", ArtistGroupListView.as_view(), name="artist-group-list"),
    path("artist-groups/<int:artist_group_id>/", ArtistGroupDetailView.as_view(), name="artist-group-detail"),
    path("artist-groups/<int:group_id>/members/add/", ArtistGroupMemberAddView.as_view(), name="artist-group-member-add"),  # 기존 아티스트를 아티스트그룹에 추가
    path("artist-groups/<int:group_id>/members/create/", ArtistGroupMemberCreateView.as_view(), name="artist-group-member-create"),  # 아티스트그룹 생성시 아티스트들을 추가해서 생성
    path("artist-groups/<int:group_id>/members/<int:artist_id>/delete/", ArtistGroupMemberDeleteView.as_view(), name="artist-group-member-delete"),
    path("staff/artist-and-groups/", StaffArtistAndGroupListView.as_view(), name="staff-artists-and-group-list"),
]
