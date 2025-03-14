from django.core.exceptions import ValidationError  # 유효성 검사 에러 확인
from django.test import TestCase  # Django 테스트 케이스 기능 사용
from django.utils import timezone  # 현재 시간을 위해

from app.accounts.models import User
from app.artists.models import Artist, ArtistGroup
from app.schedule.models import Schedule

from .models import Advertisement, Favorites, Likes, Notifications


# -------------------------------
# Advertisement 모델 테스트
# -------------------------------
class AdvertisementModelTests(TestCase):
    def test_str_representation(self):
        """
        광고(Advertisement)의 __str__ 메서드가 '광고 타입 - 광고 상태' 형식으로 반환되는지 검증합니다.
        """
        ad = Advertisement.objects.create(
            advertisement_type="Banner",
            status=True,
            sent_at=timezone.now(),
            image_url="http://example.com/ad.jpg",
            link_url="http://example.com",
            start_date=timezone.now(),
            end_date=timezone.now(),
        )
        self.assertEqual(str(ad), "Banner - True")


# -------------------------------
# Likes 모델 테스트
# -------------------------------
class LikesModelTests(TestCase):
    def setUp(self):
        """
        테스트에 필요한 User, Artist, ArtistGroup 객체를 생성합니다.
        """
        # 최소한의 필드로 User 생성
        self.user = User.objects.create_user(email="user@example.com", password="testpass", nickname="User1")
        # Artist 생성 (필수 필드 채워넣기)
        self.artist = Artist.objects.create(
            id=1,
            artist_name="Test Artist",
            artist_gruop="Test Group",  # DB의 오타 필드 그대로 사용
            artist_agency="Test Agency",
            artist_insta="insta",
            artist_groups_id=1,
            key=100,  # 예시로 정수값 사용
        )
        # ArtistGroup 생성
        self.artist_group = ArtistGroup.objects.create(
            id=1,
            artist_group="Test ArtistGroup",
            artist_agency="Test Agency",
            group_insta="insta",
            key="AG100",  # 예시로 문자열 사용
        )

    def test_likes_with_artist_only(self):
        """
        좋아요(Likes)를 아티스트만 지정하여 생성할 경우, 유효성 검사를 통과하고 __str__ 결과가 올바른지 검증합니다.
        """
        like = Likes(user=self.user, artist=self.artist, artist_group=None)
        # full_clean()를 호출해 clean() 메서드 검증
        try:
            like.full_clean()
        except ValidationError:
            self.fail("Likes with artist only raised ValidationError unexpectedly!")
        like.save()
        expected_str = f"{self.user} - {self.artist} - No Group"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_artist_group_only(self):
        """
        좋아요를 아티스트 그룹만 지정하여 생성할 경우의 유효성 및 __str__ 반환값을 검증합니다.
        """
        like = Likes(user=self.user, artist=None, artist_group=self.artist_group)
        try:
            like.full_clean()
        except ValidationError:
            self.fail("Likes with artist_group only raised ValidationError unexpectedly!")
        like.save()
        expected_str = f"{self.user} - No Artist - {self.artist_group}"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_both_fields(self):
        """
        좋아요를 아티스트와 아티스트 그룹 모두 지정할 경우, (최종 clean()에서는 둘 다 채워진 경우 에러를 발생시키지 않으므로)
        정상 생성되고 __str__ 메서드가 올바르게 동작하는지 검증합니다.
        """
        like = Likes(user=self.user, artist=self.artist, artist_group=self.artist_group)
        try:
            like.full_clean()
        except ValidationError:
            self.fail("Likes with both fields raised ValidationError unexpectedly!")
        like.save()
        expected_str = f"{self.user} - {self.artist} - {self.artist_group}"
        self.assertEqual(str(like), expected_str)

    def test_likes_with_neither_field(self):
        """
        아티스트와 아티스트 그룹 모두 지정하지 않은 경우, ValidationError가 발생하는지 검증합니다.
        """
        like = Likes(user=self.user, artist=None, artist_group=None)
        with self.assertRaises(ValidationError):
            like.full_clean()


# -------------------------------
# Favorites 모델 테스트
# -------------------------------
class FavoritesModelTests(TestCase):
    def setUp(self):
        """
        Favorites 테스트를 위한 User와 Schedule 객체를 생성합니다.
        """
        self.user = User.objects.create_user(email="favuser@example.com", password="pass", nickname="FavUser")
        # Schedule 생성: 필요한 필드는 최소값으로 채워 넣습니다.
        self.schedule = Schedule.objects.create(
            id=1,
            is_active=True,
            title="Test Schedule",
            description="Description",
            start_date=timezone.now(),
            end_date=timezone.now(),
            location="Test Location",
            artist_id=1,  # 임의의 값
            user_id=self.user.id,
            map_id=1,  # 임의의 값
            artist_groups_id=1,  # 임의의 값
            image_id=1,  # 임의의 값
        )

    def test_favorites_str(self):
        """
        즐겨찾기(Favorites)의 __str__ 메서드가 '사용자 - 일정' 형식으로 반환되는지 검증합니다.
        """
        fav = Favorites.objects.create(user=self.user, schedule=self.schedule)
        expected_str = f"{self.user} - {self.schedule}"
        self.assertEqual(str(fav), expected_str)


# -------------------------------
# Notifications 모델 테스트
# -------------------------------
class NotificationsModelTests(TestCase):
    def setUp(self):
        """
        Notifications 테스트를 위해 User, Likes, Favorites 객체를 생성합니다.
        """
        self.user = User.objects.create_user(email="notifuser@example.com", password="pass", nickname="NotifUser")
        # 생성용 dummy Artist 및 ArtistGroup
        self.artist = Artist.objects.create(
            id=2,
            artist_name="Notif Artist",
            artist_gruop="Group",
            artist_agency="Agency",
            artist_insta="insta",
            artist_groups_id=2,
            key=200,
        )
        self.artist_group = ArtistGroup.objects.create(
            id=2, artist_group="Notif ArtistGroup", artist_agency="Agency", group_insta="insta", key="AG200"
        )
        # Likes 객체 생성 (아티스트 전용 좋아요)
        self.like = Likes.objects.create(user=self.user, artist=self.artist, artist_group=None)
        # Schedule 생성: dummy 값 할당
        self.schedule = Schedule.objects.create(
            id=2,
            is_active=True,
            title="Notif Schedule",
            description="Desc",
            start_date=timezone.now(),
            end_date=timezone.now(),
            location="Location",
            artist_id=2,
            user_id=self.user.id,
            map_id=2,
            artist_groups_id=2,
            image_id=2,
        )
        # Favorites 객체 생성
        self.favorite = Favorites.objects.create(user=self.user, schedule=self.schedule)

    def test_notifications_str(self):
        """
        알림(Notifications)의 __str__ 메서드가 '알림 활성 여부 - 좋아요 - 즐겨찾기' 형식으로 반환되는지 검증합니다.
        """
        notif = Notifications.objects.create(is_active=True, likes=self.like, favorites=self.favorite)
        expected_str = f"True - {self.like} - {self.favorite}"
        self.assertEqual(str(notif), expected_str)

    def test_notifications_with_null_relations(self):
        """
        좋아요와 즐겨찾기를 지정하지 않은 알림 객체의 __str__ 메서드가 올바르게 동작하는지 검증합니다.
        """
        notif = Notifications.objects.create(is_active=False, likes=None, favorites=None)
        expected_str = "False - No Likes - No Favorites"
        self.assertEqual(str(notif), expected_str)
