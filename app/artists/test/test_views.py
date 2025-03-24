from django.test import TestCase
from rest_framework.test import APIClient

from app.accounts.models import User
from app.artists.models import Artist, ArtistGroup


class ArtistAndGroupViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="1234", nickname="User")
        self.admin = User.objects.create_superuser(email="admin@test.com", password="admin1234", nickname="Admin")

        self.artist_group = ArtistGroup.objects.create(artist_group="Group A", artist_agency="Agency A")
        self.artist = Artist.objects.create(artist_name="Artist A", artist_group=self.artist_group)

    def test_get_artist_and_group_list(self):
        response = self.client.get("/artists-and-groups/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)

    def test_get_artist_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/artists/")
        self.assertEqual(response.status_code, 200)

    def test_create_artist(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "artist_name": "New Artist",
            "artist_group_id": self.artist_group.id,
            "artist_agency": "New Agency",
            "artist_insta": "insta_handle",
        }
        response = self.client.post("/artists/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["artist_name"], "New Artist")

    def test_patch_artist(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f"/artists/{self.artist.id}/", {"artist_name": "Changed Artist"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["artist_name"], "Changed Artist")

    def test_delete_artist(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/artists/{self.artist.id}/")
        self.assertEqual(response.status_code, 204)

    def test_get_artist_group_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/artist-groups/")
        self.assertEqual(response.status_code, 200)

    def test_create_artist_group(self):
        self.client.force_authenticate(user=self.admin)
        data = {"artist_group": "Group B", "artist_agency": "Agency B"}
        response = self.client.post("/artist-groups/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["artist_group"], "Group B")

    def test_patch_artist_group(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/artist-groups/{self.artist_group.id}/", {"artist_group": "Updated Group"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["artist_group"], "Updated Group")

    def test_delete_artist_group(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/artist-groups/{self.artist_group.id}/")
        self.assertEqual(response.status_code, 204)
