from django.test import TestCase
from app.artists.models import Artist, ArtistGroup

class ArtistGroupModelTest(TestCase):
    def setUp(self):
        self.artist_group = ArtistGroup.objects.create(
            artist_group="test_group",  # 아티스트 그룹 이름
            artist_agency="test_agency",  # 소속사 이름
            group_insta="test_insta",  # 인스타그램 계정
            image_url="artist_groups/test_group_image.jpg"  # 그룹 이미지 URL 설정
        )

    def test_str_method(self):
        self.assertEqual(str(self.artist_group), "test_group")

class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist_group = ArtistGroup.objects.create(
            artist_group="test_group",  # 아티스트 그룹 이름
            artist_agency="test_agency",  # 소속사 이름
            group_insta="test_insta",  # 인스타그램 계정
            image_url="artist_groups/test_group_image.jpg"  # 그룹 이미지 URL 설정
        )
        self.artist = Artist.objects.create(
            artist_name="test_artist",  # 아티스트 이름
            artist_group=self.artist_group,  # 아티스트 그룹화
            artist_agency="test_agency",  # 소속사 이름
            artist_insta="test_insta",  # 인스타그램 계정
            image_url="artists/test_artist_image.jpg"  # 아티스트 이미지 URL 설정
        )

    def test_str_method(self):
        self.assertEqual(str(self.artist), "test_artist")

    def test_artist_group_relationship(self):
        self.assertEqual(self.artist.artist_group, self.artist_group)