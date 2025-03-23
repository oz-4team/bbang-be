from django.contrib.auth import get_user_model  # 사용자 모델을 가져오기 위한 함수
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner  # 이메일 인증 및 비밀번호 재설정 토큰 생성을 위한 서명 생성기
from django.test import TestCase  # Django 기본 테스트 클래스
from rest_framework import status  # HTTP 응답 상태 코드
from rest_framework.test import APIClient  # API 테스트 클라이언트
from rest_framework_simplejwt.tokens import RefreshToken  # JWT 토큰을 다루기 위한 모듈

# 기본 사용자 모델을 가져옴
User = get_user_model()


# 유저 관련 view 테스트
class UserAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()  # API 요청을 위한 클라이언트 생성
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", nickname="testuser", is_active=True  # 계정 활성화
        )

    def test_register(self):
        url = "/register/"  # 회원가입 엔드포인트
        data = {"email": "testuser1@example.com", "password": "testpassword", "nickname": "testuser"}
        response = self.client.post(url, data)  # POST 요청
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("회원가입 성공", response.json()["message"])

    def test_verify_email(self):
        signer = TimestampSigner()  # 서명 생성기 생성
        token = signer.sign(self.user.pk)  # 사용자 pk를 이용해 토큰 생성

        url = f"/verify-email/?token={token}"  # 이메일 인증 엔드포인트
        response = self.client.get(url)  # GET 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "이메일 인증이 완료되었습니다.")
        self.user.refresh_from_db()  # DB에서 최신 정보 불러오기
        self.assertTrue(self.user.is_active)

    def test_login(self):
        url = "/login/"  # 로그인 엔드포인트
        data = {"email": "testuser@example.com", "password": "testpassword"}
        response = self.client.post(url, data)  # 로그인 POST 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

        # 로그인 시 반환되는 JSON에 기본 이미지 URL이 포함되어 있는지 확인
        json_data = response.json()
        self.assertIn("image_url", json_data)
        self.assertIn("profile_images/default_profile_image.jpg", json_data["image_url"])

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)  # JWT refresh 토큰 생성
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")  # 인증 헤더 설정

        url = "/logout/"  # 로그아웃 엔드포인트
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data)  # 로그아웃 POST 요청

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.json()["message"], "로그아웃 성공.")

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 프로필 조회 엔드포인트
        response = self.client.get(url)  # GET 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_data = response.json()
        self.assertEqual(json_data["email"], self.user.email)
        # 프로필 조회 시 image_url 필드 검증
        self.assertIn("image_url", json_data)
        self.assertIn("profile_images/default_profile_image.jpg", json_data["image_url"])

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 프로필 업데이트 엔드포인트
        data = {"nickname": "UpdatedNick"}
        response = self.client.patch(url, data)  # PATCH 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "UpdatedNick")

    def test_delete_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 회원 탈퇴 엔드포인트
        response = self.client.delete(url)  # DELETE 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "회원탈퇴가 완료되었습니다.")
        self.assertFalse(User.objects.filter(email="testuser@example.com").exists())


# 비밀번호 재설정 view 테스트
class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()  # API 클라이언트 생성
        self.user = User.objects.create_user(email="userreset@example.com", password="testpassword", is_active=True)

    def test_request_password_reset(self):
        url = "/password-reset/request/"  # 비밀번호 재설정 요청 엔드포인트
        data = {"email": "userreset@example.com"}
        response = self.client.post(url, data)  # POST 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "비밀번호 재설정 링크가 이메일로 전송되었습니다.")

    def test_reset_password(self):
        signer = TimestampSigner()  # 서명 생성기 생성
        token = signer.sign(self.user.pk)  # 사용자 pk를 이용해 토큰 생성

        url = "/password-reset/reset/"  # 비밀번호 재설정 엔드포인트
        data = {"token": token, "password": "newpassword"}
        response = self.client.post(url, data)  # POST 요청

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "비밀번호가 성공적으로 변경되었습니다.")

        # 변경된 비밀번호로 로그인 테스트
        login_url = "/login/"
        login_data = {"email": "userreset@example.com", "password": "newpassword"}
        login_response = self.client.post(login_url, login_data)

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)


#
# class RealS3UploadTestCase(TestCase):  # S3 연결 테스트 (성공)
#     def test_upload_image_to_s3_real(self):
#         # 테스트용 이미지 데이터 생성
#         image_content = b'real test image data'
#         image_file = SimpleUploadedFile("real_test.jpg", image_content, content_type="image/jpeg")
#         user = User.objects.create_user(email="realtest@example.com", password="realpass", nickname="realtest")
#         user.image_url.save("real_test.jpg", image_file)
#         # 실제 S3에 파일이 업로드되었는지 확인
#         self.assertTrue(default_storage.exists(user.image_url.name))
#         # 반환된 URL 형식 검증 (실제 S3 URL 확인)
#         self.assertTrue(user.image_url.url.startswith("https://"))
