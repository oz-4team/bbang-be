from django.test import TestCase, Client
from django.urls import reverse  # URL reverse function for dynamic URL resolution
from app.artists.models import Artist, ArtistGroup

# ArtistAndGroupListView에 대한 테스트 클래스입니다.  # 뷰 테스트 클래스 정의
class ArtistAndGroupListViewTest(TestCase):
    def setUp(self):  # 각 테스트 실행 전 필요한 초기 데이터 설정
        self.client = Client()  # 테스트 클라이언트 인스턴스 생성
        # 테스트용 ArtistGroup 인스턴스를 생성합니다.  # ArtistGroup 객체 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test Group",  # 테스트용 그룹명 지정
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            group_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artist_groups/test_group_image.jpg"  # 테스트용 이미지 URL 지정
        )
        # 테스트용 Artist 인스턴스를 생성합니다.  # Artist 객체 생성
        self.artist = Artist.objects.create(
            artist_name="Test Artist",  # 테스트용 아티스트 이름 지정
            artist_group=self.artist_group,  # 생성한 ArtistGroup과 연결
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            artist_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artists/test_artist_image.jpg"  # 테스트용 이미지 URL 지정
        )

    def test_get_artists_and_groups(self):  # GET 요청에 대한 테스트 메서드
        # '/api/artists-groups/' URL은 ArtistAndGroupListView에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 지정
        url = reverse('artist-and-group-list')  # reverse()를 사용하여 URL을 생성
        response = self.client.get(url)  # GET 요청 전송
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertIn("artists", data)  # 응답 데이터에 "artists" 키가 존재하는지 검증
        self.assertIn("artist_groups", data)  # 응답 데이터에 "artist_groups" 키가 존재하는지 검증
        self.assertEqual(len(data["artists"]), 1)  # 반환된 아티스트 리스트의 길이가 1인지 검증
        self.assertEqual(len(data["artist_groups"]), 1)  # 반환된 아티스트 그룹 리스트의 길이가 1인지 검증


# ArtistListView에 대한 테스트 클래스입니다.  # 개별 아티스트 조회/생성 뷰 테스트 클래스 정의
class ArtistListViewTest(TestCase):
    def setUp(self):  # 테스트 실행 전 초기 데이터 설정
        self.client = Client()  # 테스트 클라이언트 인스턴스 생성
        # 테스트용 ArtistGroup 인스턴스 생성  # ArtistListView에서 artist_group 연관성을 테스트하기 위한 그룹 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test Group",  # 테스트용 그룹명 지정
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            group_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artist_groups/test_group_image.jpg"  # 테스트용 이미지 URL 지정
        )
        # 테스트용 Artist 인스턴스 생성  # 기본 Artist 객체 생성
        self.artist = Artist.objects.create(
            artist_name="Test Artist",  # 테스트용 아티스트 이름 지정
            artist_group=self.artist_group,  # 생성한 ArtistGroup과 연결
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            artist_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artists/test_artist_image.jpg"  # 테스트용 이미지 URL 지정
        )

    def test_get_artist_list(self):  # GET 요청으로 아티스트 전체 조회 테스트
        # '/api/artists/' URL은 ArtistListView에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 지정
        url = reverse('artist-list')  # reverse()를 사용하여 URL을 생성
        response = self.client.get(url)  # GET 요청 전송
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(len(data), 1)  # 반환된 아티스트 리스트의 길이가 1인지 검증

    def test_post_artist_with_group(self):  # POST 요청으로 아티스트 생성 테스트 (artist_group 포함)
        # '/api/artists/' URL은 ArtistListView의 POST 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 지정
        payload = {  # 새로운 아티스트 생성에 필요한 데이터를 정의합니다.
            "artist_name": "New Artist",  # 새로 생성할 아티스트의 이름 지정
            "artist_group_id": self.artist_group.id,  # 생성할 아티스트에 연결할 그룹 ID 지정
            "artist_agency": "New Agency",  # 새로 생성할 아티스트의 소속사 지정
            "artist_insta": "new_insta"  # 새로 생성할 아티스트의 인스타그램 계정 지정
        }
        url = reverse('artist-list')  # reverse()를 사용하여 URL을 생성
        response = self.client.post(url, data=payload)  # POST 요청 전송하여 새 아티스트 생성
        self.assertEqual(response.status_code, 201)  # 응답 상태 코드가 201(CREATED) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_name"], "New Artist")  # 반환된 아티스트 이름이 올바른지 검증
        self.assertEqual(data["artist_group"]["id"], self.artist_group.id)  # 반환된 artist_group 필드가 올바른 그룹 ID인지 검증


# ArtistDetailView에 대한 테스트 클래스입니다.  # 개별 아티스트 상세 조회/수정/삭제 뷰 테스트 클래스 정의
class ArtistDetailViewTest(TestCase):
    def setUp(self):  # 테스트 실행 전 초기 데이터 설정
        self.client = Client()  # 테스트 클라이언트 인스턴스 생성
        # 테스트용 ArtistGroup 인스턴스 생성  # 아티스트 상세 테스트를 위한 그룹 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test Group",  # 테스트용 그룹명 지정
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            group_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artist_groups/test_group_image.jpg"  # 테스트용 이미지 URL 지정
        )
        # 테스트용 Artist 인스턴스 생성  # 상세 테스트를 위한 아티스트 객체 생성
        self.artist = Artist.objects.create(
            artist_name="Test Artist",  # 테스트용 아티스트 이름 지정
            artist_group=self.artist_group,  # 생성한 ArtistGroup과 연결
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            artist_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artists/test_artist_image.jpg"  # 테스트용 이미지 URL 지정
        )

    def test_get_artist_detail(self):  # GET 요청으로 개별 아티스트 상세 조회 테스트
        # '/api/artists/<artist_id>/' URL은 ArtistDetailView의 GET 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-detail', kwargs={'artist_id': self.artist.id})  # reverse()를 사용하여 URL 생성
        response = self.client.get(url)  # GET 요청 전송
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_name"], "Test Artist")  # 반환된 아티스트 이름이 올바른지 검증

    def test_patch_artist_detail(self):  # PATCH 요청으로 개별 아티스트 수정 테스트
        # '/api/artists/<artist_id>/' URL은 ArtistDetailView의 PATCH 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-detail', kwargs={'artist_id': self.artist.id})  # reverse()를 사용하여 URL 생성
        payload = {  # 수정할 데이터를 정의합니다.
            "artist_name": "Updated Artist",  # 업데이트할 새 아티스트 이름 지정
            "artist_group_id": None  # 아티스트 그룹 제거를 위해 None 지정
        }
        response = self.client.patch(url, data=payload, content_type='application/json')  # PATCH 요청 전송 (JSON 데이터 형식 지정)
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_name"], "Updated Artist")  # 업데이트된 아티스트 이름이 올바른지 검증
        self.assertIsNone(data["artist_group"])  # 아티스트 그룹 필드가 None으로 업데이트 되었는지 검증

    def test_delete_artist_detail(self):  # DELETE 요청으로 개별 아티스트 삭제 테스트
        # '/api/artists/<artist_id>/' URL은 ArtistDetailView의 DELETE 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-detail', kwargs={'artist_id': self.artist.id})  # reverse()를 사용하여 URL 생성
        response = self.client.delete(url)  # DELETE 요청 전송
        self.assertEqual(response.status_code, 204)  # 응답 상태 코드가 204(NO CONTENT) 인지 검증
        # 데이터베이스에서 해당 아티스트 인스턴스가 삭제되었는지 확인합니다.  # 삭제 검증을 위해 DB 조회
        self.assertFalse(Artist.objects.filter(id=self.artist.id).exists())  # 아티스트 객체가 존재하지 않음을 검증


# ArtistGroupListView에 대한 테스트 클래스입니다.  # 그룹 아티스트 전체 조회/생성 뷰 테스트 클래스 정의
class ArtistGroupListViewTest(TestCase):
    def setUp(self):  # 테스트 실행 전 초기 데이터 설정
        self.client = Client()  # 테스트 클라이언트 인스턴스 생성
        # 테스트용 ArtistGroup 인스턴스를 생성합니다.  # 그룹 객체 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test Group",  # 테스트용 그룹명 지정
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            group_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artist_groups/test_group_image.jpg"  # 테스트용 이미지 URL 지정
        )

    def test_get_artist_group_list(self):  # GET 요청으로 그룹 전체 조회 테스트
        # '/api/artist-groups/' URL은 ArtistGroupListView의 GET 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 지정
        url = reverse('artist-group-list')  # reverse()를 사용하여 URL을 생성
        response = self.client.get(url)  # GET 요청 전송
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(len(data), 1)  # 반환된 그룹 리스트의 길이가 1인지 검증

    def test_post_artist_group(self):  # POST 요청으로 새 그룹 생성 테스트
        # '/api/artist-groups/' URL은 ArtistGroupListView의 POST 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 지정
        payload = {  # 새 그룹 생성을 위한 데이터를 정의합니다.
            "artist_group": "New Group",  # 새로 생성할 그룹명 지정
            "artist_agency": "New Agency",  # 새로 생성할 소속사 지정
            "group_insta": "new_insta",  # 새로 생성할 인스타그램 계정 지정
        }
        url = reverse('artist-group-list')  # reverse()를 사용하여 URL을 생성
        response = self.client.post(url, data=payload)  # POST 요청 전송하여 그룹 생성
        self.assertEqual(response.status_code, 201)  # 응답 상태 코드가 201(CREATED) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_group"], "New Group")  # 반환된 그룹명이 올바른지 검증


# ArtistGroupDetailView에 대한 테스트 클래스입니다.  # 개별 그룹 상세 조회/수정/삭제 뷰 테스트 클래스 정의
class ArtistGroupDetailViewTest(TestCase):
    def setUp(self):  # 테스트 실행 전 초기 데이터 설정
        self.client = Client()  # 테스트 클라이언트 인스턴스 생성
        # 테스트용 ArtistGroup 인스턴스를 생성합니다.  # 그룹 객체 생성
        self.artist_group = ArtistGroup.objects.create(
            artist_group="Test Group",  # 테스트용 그룹명 지정
            artist_agency="Test Agency",  # 테스트용 소속사 지정
            group_insta="test_insta",  # 테스트용 인스타그램 계정 지정
            image_url="artist_groups/test_group_image.jpg"  # 테스트용 이미지 URL 지정
        )

    def test_get_artist_group_detail(self):  # GET 요청으로 개별 그룹 상세 조회 테스트
        # '/api/artist-groups/<artist_group_id>/' URL은 ArtistGroupDetailView의 GET 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-group-detail', kwargs={'artist_group_id': self.artist_group.id})  # reverse()를 사용하여 URL 생성
        response = self.client.get(url)  # GET 요청 전송
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_group"], "Test Group")  # 반환된 그룹명이 올바른지 검증

    def test_patch_artist_group_detail(self):  # PATCH 요청으로 개별 그룹 수정 테스트
        # '/api/artist-groups/<artist_group_id>/' URL은 ArtistGroupDetailView의 PATCH 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-group-detail', kwargs={'artist_group_id': self.artist_group.id})  # reverse()를 사용하여 URL 생성
        payload = {  # 수정할 데이터를 정의합니다.
            "artist_group": "Updated Group"  # 업데이트할 새 그룹명 지정
        }
        response = self.client.patch(url, data=payload, content_type='application/json')  # PATCH 요청 전송 (JSON 데이터 형식 지정)
        self.assertEqual(response.status_code, 200)  # 응답 상태 코드가 200(OK) 인지 검증
        data = response.json()  # 응답 내용을 JSON 형식으로 파싱
        self.assertEqual(data["artist_group"], "Updated Group")  # 업데이트된 그룹명이 올바른지 검증

    def test_delete_artist_group_detail(self):  # DELETE 요청으로 개별 그룹 삭제 테스트
        # '/api/artist-groups/<artist_group_id>/' URL은 ArtistGroupDetailView의 DELETE 메서드에 대응한다고 가정합니다.  # 테스트할 엔드포인트 URL 구성
        url = reverse('artist-group-detail', kwargs={'artist_group_id': self.artist_group.id})  # reverse()를 사용하여 URL 생성
        response = self.client.delete(url)  # DELETE 요청 전송
        self.assertEqual(response.status_code, 204)  # 응답 상태 코드가 204(NO CONTENT) 인지 검증
        # 데이터베이스에서 해당 그룹 인스턴스가 삭제되었는지 확인합니다.  # 삭제 여부 확인을 위해 DB 조회
        self.assertFalse(ArtistGroup.objects.filter(id=self.artist_group.id).exists())  # 그룹 객체가 존재하지 않음을 검증