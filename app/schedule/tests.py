from django.test import TestCase
from django.utils.timezone import now, timedelta

from app.accounts.models import User, UserImage
from app.artists.models import Artist, ArtistGroup
from app.schedule.models import Map, Schedule, ScheduleImage

# Create your tests here.


class ScheduleModelTest(TestCase):
    def setUp(self):
        self.user_image = UserImage.objects.create(id=1)

        self.user = User.objects.create_user(email="test@test.com", nickname="test", password="1234")

        self.artist_group = ArtistGroup.objects.create(artist_group="test_group", artist_agency="test_agency")

        self.artist = Artist.objects.create(
            artist_name="test_artist", artist_group=self.artist_group, artist_agency="test_agency"
        )

        self.schedule_image = ScheduleImage.objects.create(
            image_name="schedule_image", image_url="http://example.com/schedule.jpg", image_type="jpg"
        )

        self.map = Map.objects.create(
            map_name="경복궁", map_address="서울특별시 종로구 사직로 161", latitude=37.580755, longitude=-126.976909
        )

        self.schedule = Schedule.objects.create(
            is_active=True,
            title="test_schedule",
            description="schedule_test",
            start_date=now(),
            end_date=now() + timedelta(days=1),
            location="test_location",
            artist=self.artist,
            user=self.user,
            map=self.map,
            artist_group=self.artist_group,
            image=self.schedule_image,
        )

    def test_schedule_str(self):
        self.assertEqual(str(self.schedule), "test_schedule")

    def test_schedule_artist_relationship(self):
        self.assertEqual(self.schedule.artist, self.artist)

    def test_schedule_user_relationship(self):
        self.assertEqual(self.schedule.user, self.user)

    def test_schedule_map_relationship(self):
        self.assertEqual(self.schedule.map, self.map)

    def test_schedule_artist_group_relationship(self):
        self.assertEqual(self.schedule.artist_group, self.artist_group)

    def test_schedule_image_relationship(self):
        self.assertEqual(self.schedule.image, self.schedule_image)
