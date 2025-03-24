from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from app.artists.models import Artist, ArtistGroup
from app.content.models import Advertisement, Favorites, Likes, Notifications
from app.schedule.models import Schedule

User = get_user_model()


class ContentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass", nickname="tester")  # 유저 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Group1", artist_agency="Agency", group_insta="insta"
        )  # 아티스트 그룹 생성
        self.artist = Artist.objects.create(
            artist_name="Artist1", artist_group=self.artist_group, artist_agency="Agency", artist_insta="insta"
        )  # 아티스트 생성
        self.schedule = Schedule.objects.create(title="Schedule1", user=self.user, artist=self.artist)  # 일정 생성

    def test_advertisement_creation(self):
        ad = Advertisement.objects.create(advertisement_type="Banner", status=True)
        self.assertEqual(str(ad), "Banner - True")

    def test_likes_creation_and_validation(self):
        like = Likes.objects.create(user=self.user, artist=self.artist)
        like.full_clean()  # Should not raise
        self.assertIn("Artist1", str(like))

        like_invalid = Likes(user=self.user)
        with self.assertRaises(ValidationError):
            like_invalid.full_clean()

    def test_favorites_creation(self):
        fav = Favorites.objects.create(user=self.user, schedule=self.schedule)
        self.assertIn("Schedule1", str(fav))

    def test_notifications_str(self):
        like = Likes.objects.create(user=self.user, artist=self.artist)
        fav = Favorites.objects.create(user=self.user, schedule=self.schedule)
        notif = Notifications.objects.create(is_active=True, likes=like, favorites=fav)
        self.assertIn("True", str(notif))
        self.assertIn("tester", str(notif))
