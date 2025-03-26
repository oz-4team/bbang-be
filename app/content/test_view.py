from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from app.artists.models import Artist, ArtistGroup
from app.schedule.models import Schedule

User = get_user_model()


class LikeFavoriteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="testuser")
        self.client.force_authenticate(user=self.user)

        self.artist_group = ArtistGroup.objects.create(
            artist_group="TestGroup", artist_agency="TestAgency", group_insta="insta"
        )
        self.artist = Artist.objects.create(
            artist_name="TestArtist", artist_group=self.artist_group, artist_agency="TestAgency", artist_insta="insta"
        )
        self.schedule = Schedule.objects.create(
            is_active=True,
            title="Test Schedule",
            description="Desc",
            start_date=timezone.now(),
            end_date=timezone.now(),
            location="Loc",
            artist=self.artist,
            artist_group=self.artist_group,
            user=self.user,
        )

    def test_like_create_and_delete(self):
        # 좋아요 생성
        response = self.client.post("/like/", {"artist_id": self.artist.id})
        self.assertEqual(response.status_code, 201)
        like_id = response.data["like_id"]

        # 좋아요 단건 조회
        response = self.client.get(f"/Alllike/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # 좋아요 삭제
        response = self.client.delete("/like/", {"like_id": like_id}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_favorite_create_and_delete(self):
        # 즐겨찾기 생성
        response = self.client.post("/favorite/", {"schedule_id": self.schedule.id})
        self.assertEqual(response.status_code, 201)
        favorite_id = response.data["favorite_id"]

        # 즐겨찾기 단건 조회
        response = self.client.get("/Allfavorite/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # 즐겨찾기 삭제
        response = self.client.delete("/favorite/", {"schedule_id": self.schedule.id}, format="json")
        self.assertEqual(response.status_code, 200)
