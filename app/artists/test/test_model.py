from django.test import TestCase

from app.artists.models import Artist, ArtistGroup


class ArtistGroupModelTest(TestCase):
    def setUp(self):
        self.artist_group = ArtistGroup.objects.create(
            artist_group="TestGroup",
            artist_agency="TestAgency",
            group_insta="group_insta",
            image_url="artist_groups/test.jpg",
        )

    def test_str_method(self):
        self.assertEqual(str(self.artist_group), "TestGroup")

    def test_fields(self):
        self.assertEqual(self.artist_group.artist_agency, "TestAgency")
        self.assertEqual(self.artist_group.group_insta, "group_insta")
        self.assertEqual(self.artist_group.image_url.name, "artist_groups/test.jpg")


class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist_group = ArtistGroup.objects.create(artist_group="TestGroup", artist_agency="TestAgency")
        self.artist = Artist.objects.create(
            artist_name="TestArtist",
            artist_group=self.artist_group,
            artist_agency="TestAgency",
            artist_insta="artist_insta",
            image_url="artists/test.jpg",
        )

    def test_str_method(self):
        self.assertEqual(str(self.artist), "TestArtist")

    def test_fields(self):
        self.assertEqual(self.artist.artist_agency, "TestAgency")
        self.assertEqual(self.artist.artist_insta, "artist_insta")
        self.assertEqual(self.artist.image_url.name, "artists/test.jpg")

    def test_artist_group_relationship(self):
        self.assertEqual(self.artist.artist_group.artist_group, "TestGroup")
