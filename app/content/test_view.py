from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.artists.models import Artist, ArtistGroup
from app.content.models import Favorites, Likes, Notifications
from app.schedule.models import Schedule

User = get_user_model()


class ContentViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="testuser@test.com", password="testpass")  # 테스트용 사용자
        self.client.force_authenticate(user=self.user)  # 사용자 인증된 상태로

        self.artist = Artist.objects.create(artist_name="Test Artist")  # 테스트용 아티스트
        self.artist_group = ArtistGroup.objects.create(  # 테스트용 아티스트 그룹
            artist_group="Test Group", artist_agency="Test Agency", group_insta="test_insta"
        )

        self.schedule = Schedule.objects.create(  # 테스트용 일정
            title="Original Title",
            description="Original Description",
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        # 각 엔드포인트 설정
        self.like_url = reverse("like")
        self.favorite_url = reverse("favorite")
        self.schedule_create_url = reverse("schedule-create-notification")
        self.schedule_update_url = reverse("schedule-update-notification")

    def test_like_create_and_delete(self):
        data = {"artist_id": self.artist.id}
        response = self.client.post(self.like_url, data, format="json")  # 좋아요생성
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 상태코드 확인
        like_id = response.data.get("like_id")  # 좋아요 아이디 가져와서
        self.assertIsNotNone(like_id)  # 아이디 존재하는지 확인

        delete_data = {"like_id": like_id}
        response = self.client.delete(self.like_url, delete_data, format="json")  # 좋아요 삭제
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태코드 확인

    def test_favorite_create_and_delete(self):
        data = {"schedule_id": self.schedule.id}
        response = self.client.post(self.favorite_url, data, format="json")  # 즐겨찾기 생성
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 상태코드 확인
        favorite_id = response.data.get("favorite_id")  # 아이디 가져옴
        self.assertIsNotNone(favorite_id)  # 존재하는지 확인

        delete_data = {"favorite_id": favorite_id}
        response = self.client.delete(self.favorite_url, delete_data, format="json")  # 즐겨찾기 삭제
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태코드 확인

    def test_schedule_create_notification_with_artist(self):
        like = Likes.objects.create(user=self.user, artist=self.artist)
        mail.outbox = []  # 빈 리스트 생성해 이메일 전송 확인

        data = {
            "title": "New Schedule",
            "description": "Schedule Description",  # 아티스트 좋아요 누름
            "artist_id": self.artist.id,
        }
        response = self.client.post(self.schedule_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 상태코드 확인
        self.assertIsNotNone(response.data.get("schedule_id"))  # 일정 아이디 존재하는지 확인
        self.assertTrue(len(mail.outbox) > 0)  # 이메일 전송 확인
        self.assertTrue(Notifications.objects.filter(likes=like).exists())  # 웹 알림 확인

    def test_schedule_create_notification_with_artist_group(self):
        like = Likes.objects.create(user=self.user, artist_group=self.artist_group)
        mail.outbox = []  # 빈 리스트 생성해 이메일 전송 확인

        data = {
            "title": "Group Schedule",
            "description": "Group Schedule Description",  # 아티스트 그룹 좋아요 누름
            "artist_group_id": self.artist_group.id,
        }
        response = self.client.post(self.schedule_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 상태코드 확인
        self.assertIsNotNone(response.data.get("schedule_id"))  # 아이디 존재하는지 확인
        self.assertTrue(len(mail.outbox) > 0)  # 이메일 전송 확인
        self.assertTrue(Notifications.objects.filter(likes=like).exists())  # 웹 알림 확인

    def test_schedule_update_notification(self):
        favorite = Favorites.objects.create(user=self.user, schedule=self.schedule)
        mail.outbox = []  # 빈 리스트 생성해 이메일 전송 확인

        data = {
            "schedule_id": self.schedule.id,
            "title": "Updated Title",  # 일정 즐겨찾기 누름
            "description": "Updated Description",
        }
        response = self.client.patch(self.schedule_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태코드 확인
        self.schedule.refresh_from_db()  # 데이터베이스 새로고침
        self.assertEqual(self.schedule.title, "Updated Title")  # 일정 제목이 같은지 확인
        self.assertTrue(len(mail.outbox) > 0)  # 이메일 전송 확인
        self.assertTrue(Notifications.objects.filter(favorites=favorite).exists())  # 웹 알림 확인
