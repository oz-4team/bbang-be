import pytest
from django.test import TestCase

from app.artists.models import Artist, ArtistGroup, ArtistGroupImage, ArtistImage

# Create your tests here.


class ArtistModelTest(TestCase):
    def setUp(self):
        self.group_image = ArtistGroupImage.objects.create(
            image_name="test_group_image", image_url="http://example.com/group.jpg", image_type="jpg"
        )

        self.artist_group = ArtistGroup.objects.create(
            artist_group="test_group", artist_agency="test_agency", group_insta="test_insta", image=self.group_image
        )

        self.artist_image = ArtistImage.objects.create(
            image_name="test_image", image_url="http://example.com/artist.jpg", image_type="jpg"
        )

        self.artist = Artist.objects.create(
            artist_name="test_artist",
            artist_group=self.artist_group,
            artist_agency="test_agency",
            artist_insta="artist_insta",
            image=self.artist_image,
        )

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "test_artist")

    def test_artist_group_str(self):
        self.assertEqual(str(self.artist_group), "test_group")

    def test_artist_image_str(self):
        self.assertEqual(str(self.artist_image), "test_image")

    def test_artist_group_image_str(self):
        self.assertEqual(str(self.group_image), "test_group_image")

    def test_artist_group_relationship(self):
        self.assertEqual(self.artist.artist_group, self.artist_group)

    def test_artist_image_relationship(self):
        self.assertEqual(self.artist.image, self.artist_image)

    def test_artist_group_image_relationship(self):
        self.assertEqual(self.artist_group.image, self.group_image)
