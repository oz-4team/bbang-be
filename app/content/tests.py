from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.accounts.models import User, UserImage
from app.artists.models import Artist, ArtistGroup
from app.schedule.models import Map, Schedule

from .models import Advertisement, Favorites, Likes, Notifications


# Advertisement 모델 테스트
class AdvertisementModelTests(TestCase):
    def test_str_representation(self):
        ad = Advertisement.objects.create(  # 광고 생성
            advertisement_type="Banner",
            status=True,
            sent_at=timezone.now(),
            image_url="http://example.com/ad.jpg",
            link_url="http://example.com",
            start_date=timezone.now(),
            end_date=timezone.now(),
        )
        self.assertEqual(str(ad), "Banner - True")  # 광고 메서드가 광고타입 -  광고 상태 형식인지 테스트


# Likes 모델 테스트
class LikesModelTests(TestCase):
    def setUp(self):
        # UserImage 생성
        self.user_image = UserImage.objects.create(
            image_name="TestUserImage", image_url="http://example.com/user.jpg", image_type="jpg"
        )
        # User 생성
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass", nickname="User1", user_image=self.user_image
        )
        # ArtistGroup 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="TestGroup",
            artist_agency="TestAgency",
            group_insta="group_insta",
        )
        # Artist 생성
        self.artist = Artist.objects.create(
            artist_name="TestArtist",
            artist_group=self.artist_group,
            artist_agency="TestAgency",
            artist_insta="artist_insta",
        )

    def test_likes_with_artist_only(self):
        like = Likes(user=self.user, artist=self.artist, artist_group=None)
        try:
            like.full_clean()  # 아티스트 좋아요 시 유효성 검사 통과 테스트
        except ValidationError:
            self.fail("아티스트 지정")
        like.save()

        # __str__ 확인
        expected_str = f"{self.user} - {self.artist} - No Group"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_artist_group_only(self):
        like = Likes(user=self.user, artist=None, artist_group=self.artist_group)
        try:
            like.full_clean()  # 아티스트 그룹 좋아요 시 유효성 검사 통과 테스트
        except ValidationError:
            self.fail("아티스트그룹 지정")
        like.save()

        expected_str = f"{self.user} - No Artist - {self.artist_group}"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_both_artist_and_group(self):
        like = Likes(user=self.user, artist=self.artist, artist_group=self.artist_group)
        try:
            like.full_clean()  # 아티스트, 아티스트 그룹 좋아요 시 통과 테스트
        except ValidationError:
            self.fail("아티스트, 아티스트그룹 지정")
        like.save()

        expected_str = f"{self.user} - {self.artist} - {self.artist_group}"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_no_fields(self):
        like = Likes(
            user=self.user, artist=None, artist_group=None
        )  # 아티스트와 아티스트 그룹 모두 지정 안했을시 에러 테스트
        with self.assertRaises(ValidationError):
            like.full_clean()


# Favorites 모델 테스트
class FavoritesModelTests(TestCase):
    def setUp(self):

        # 기본 UserImage
        self.user_image = UserImage.objects.create(
            image_name="FavUserImage", image_url="http://example.com/user.jpg", image_type="jpg"
        )

        # User 생성
        self.user = User.objects.create_user(
            email="favuser@example.com", password="pass", nickname="FavUser", user_image=self.user_image
        )

        # ArtistGroup 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test ArtistGroup", artist_agency="Test Agency", group_insta="insta"
        )

        # Artist 생성
        self.artist = Artist.objects.create(
            artist_name="Test Artist",
            artist_group=self.artist_group,
            artist_agency="Test Agency",
            artist_insta="insta",
        )

        # Map 생성 (자동 PK)
        self.schedule_map = Map.objects.create(
            map_name="TestMap", map_address="123 Test St", latitude=37.5665, longitude=126.9780
        )

        # Schedule 생성
        self.schedule = Schedule.objects.create(
            is_active=True,
            title="Test Schedule",
            description="Description",
            start_date=timezone.now(),
            end_date=timezone.now(),
            location="Test Location",
            artist=self.artist,
            user=self.user,
            map=self.schedule_map,
            artist_group=self.artist_group,
        )

    def test_favorites_str(self):
        fav = Favorites.objects.create(user=self.user, schedule=self.schedule)  # 즐겨찾기 생성
        expected_str = f"{self.user} - {self.schedule}"  # 즐겨찾기 메소드가 사용자 - 일정 형식으로 반환되는지 테스트
        self.assertEqual(str(fav), expected_str)


# Notifications 모델 테스트
class NotificationsModelTests(TestCase):
    def setUp(self):
        # 기본 UserImage
        self.user_image = UserImage.objects.create(
            image_name="NotifUserImage", image_url="http://example.com/user.jpg", image_type="jpg"
        )

        # User 생성
        self.user = User.objects.create_user(
            email="notifuser@example.com", password="pass", nickname="NotifUser", user_image=self.user_image
        )

        # ArtistGroup 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Notif ArtistGroup", artist_agency="Agency", group_insta="insta"
        )

        # Artist 생성
        self.artist = Artist.objects.create(
            artist_name="Notif Artist",
            artist_group=self.artist_group,
            artist_agency="Agency",
            artist_insta="insta",
        )

        # Likes 생성
        self.like = Likes.objects.create(user=self.user, artist=self.artist, artist_group=None)

        # Map 생성
        self.schedule_map = Map.objects.create(
            map_name="Test Map", map_address="Test Test Test", latitude=11.1111, longitude=22.2222
        )

        # Schedule 생성
        self.schedule = Schedule.objects.create(
            is_active=True,
            title="test title",
            description="test",
            start_date=timezone.now(),
            end_date=timezone.now(),
            location="Location",
            artist=self.artist,
            user=self.user,
            map=self.schedule_map,
            artist_group=self.artist_group,
        )

        # Favorites 생성
        self.favorite = Favorites.objects.create(user=self.user, schedule=self.schedule)

    def test_notifications_str(self):
        notif = Notifications.objects.create(is_active=True, likes=self.like, favorites=self.favorite)  # 알림 생성
        expected_str = f"True - {self.like} - {self.favorite}"  # 형식 만들기
        self.assertEqual(
            str(notif), expected_str
        )  # 알림의 메서드가 알림활성여부 - 좋아요 - 즐겨찾기 형식으로 반환되는지 테스트
