from django.urls import path

from app.content.views import (
    AdvertisementDetailAPIView,
    AdvertisementListAPIView,
    AdvertisementManageAPIView,
    AllFavoritesAPIView,
    AllLikesAPIView,
    FavoriteAPIView,
    LikeAPIView,
    SingleLikeAPIView,
    StaffUpAPIView,
)

urlpatterns = [
    path("like/", LikeAPIView.as_view(), name="like"),
    path("Alllike/", AllLikesAPIView.as_view(), name="Alllike"),
    path("userlike/<int:like_id>/", SingleLikeAPIView.as_view(), name="userlike"),
    path("favorite/", FavoriteAPIView.as_view(), name="favorite"),
    path("Allfavorite/", AllFavoritesAPIView.as_view(), name="Allfavorite"),
    path("advertisement/list/", AdvertisementListAPIView.as_view(), name="advertisement_list"),
    path("advertisement/<int:advertisement_id>/", AdvertisementDetailAPIView.as_view(), name="advertisement_detail"),
    path("advertisement/", AdvertisementManageAPIView.as_view(), name="advertisement_manage"),
    path("authority/", StaffUpAPIView.as_view(), name="authority"),
]
