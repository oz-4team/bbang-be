from django.urls import path

from app.artists.views import (
    ArtistAndGroupListView,
    ArtistDetailView,
    ArtistGroupDetailView,
    ArtistGroupView,
    ArtistView,
)

urlpatterns = [
    path("artists-and-groups/", ArtistAndGroupListView.as_view(), name="artist-and-group-list"),
    path("artist-groups/", ArtistGroupView.as_view(), name="artist-group-list"),
    path("artist-groups/<int:artist_group_id>/", ArtistGroupDetailView.as_view(), name="artist-group-detail"),
    path("artists/", ArtistView.as_view(), name="artist-list"),
    path("artists/<int:artist_id>/", ArtistDetailView.as_view(), name="artist-detail"),
]

