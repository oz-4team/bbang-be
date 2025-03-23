from django.urls import path

from app.schedule.views import (
    ArtistGroupScheduleListView,
    ArtistGroupScheduleManageView,
    ArtistScheduleListView,
    ArtistScheduleManageView,
    FavoriteSchedulesView,
    ScheduleDetailView,
    ScheduleListView,
)

urlpatterns = [
    path("schedules/", ScheduleListView.as_view(), name="schedule-list"),
    path("schedules/artist/<int:artist_id>/", ArtistScheduleListView.as_view(), name="artist-schedule-list"),
    path(
        "schedules/artist-group/<int:artist_group_id>/",
        ArtistGroupScheduleListView.as_view(),
        name="artist-group-schedule-list",
    ),
    path("schedules/<int:schedule_id>/", ScheduleDetailView.as_view(), name="schedule-detail"),
    path("schedules/favorites/", FavoriteSchedulesView.as_view(), name="favorite-schedules"),
    path("schedules/artist/manage/", ArtistScheduleManageView.as_view(), name="artist-schedule-manage-create"),
    path(
        "schedules/artist/manage/<int:schedule_id>/",
        ArtistScheduleManageView.as_view(),
        name="artist-schedule-manage-detail",
    ),
    path(
        "schedules/artist-group/manage/",
        ArtistGroupScheduleManageView.as_view(),
        name="artist-group-schedule-manage-create",
    ),
    path(
        "schedules/artist-group/manage/<int:schedule_id>/",
        ArtistGroupScheduleManageView.as_view(),
        name="artist-group-schedule-manage-detail",
    ),
]
