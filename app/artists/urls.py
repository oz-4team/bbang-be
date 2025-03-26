from django.urls import path

from app.artists.views import (
    ArtistAndGroupListView,
    ArtistDetailView,
    ArtistGroupDetailView,
    ArtistGroupListView,
    ArtistListView, StaffArtistAndGroupListView,
)

urlpatterns = [
    path("artists-and-groups/", ArtistAndGroupListView.as_view(), name="artist-and-group-list"),
    path("artists/", ArtistListView.as_view(), name="artist-list"),
    path("artists/<int:artist_id>/", ArtistDetailView.as_view(), name="artist-detail"),
    path("artist-groups/", ArtistGroupListView.as_view(), name="artist-group-list"),
    path("artist-groups/<int:artist_group_id>/", ArtistGroupDetailView.as_view(), name="artist-group-detail"),
    path("staff/artist-and-groups/", StaffArtistAndGroupListView.as_view(), name="staff-artists-and-group-list"),
]
