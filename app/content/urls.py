from django.urls import path

from app.content.views import (
    FavoriteAPIView,
    LikeAPIView,
    ScheduleCreateNotificationAPIView,
    ScheduleUpdateNotificationAPIView,
)

urlpatterns = [
    path("like/", LikeAPIView.as_view(), name="like"),
    path("favorite/", FavoriteAPIView.as_view(), name="favorite"),
    path(
        "schedule/create-notification/",
        ScheduleCreateNotificationAPIView.as_view(),
        name="schedule-create-notification",
    ),
    path(
        "schedule/update-notification/",
        ScheduleUpdateNotificationAPIView.as_view(),
        name="schedule-update-notification",
    ),
]
