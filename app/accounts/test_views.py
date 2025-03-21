from django.contrib.auth import get_user_model  # 사용자 모델을 가져오기 위한 함수
from django.core.signing import TimestampSigner  # 이메일 인증 및 비밀번호 재설정 토큰을 위한 서명 생성기
from django.test import TestCase  # Django의 기본 테스트 클래스
from rest_framework import status  # HTTP 응답 상태 코드
from rest_framework.test import APIClient  # Django REST framework의 API 테스트 클라이언트
from rest_framework_simplejwt.tokens import RefreshToken  # JWT 토큰을 다루기 위한 모듈

# Django의 기본 사용자 모델 가져오기
User = get_user_model()


# 유저 테스트
class UserAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()  # API 요청을 위한 클라이언트 생성
        self.user = User.objects.create_user(  # 사용자 생성
            email="testuser@example.com", password="testpassword", nickname="testuser", is_active=True  # 계정 활성화
        )

    def test_register(self):
        url = "/register/"  # 엔드포인트
        data = {"email": "testuser1@example.com", "password": "testpassword", "nickname": "testuser"}  # 새로 생성
        response = self.client.post(url, data)  # POST
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # 상태 코드 확인
        self.assertIn("회원가입 성공", response.json()["message"])  # 메세지

    def test_verify_email(self):
        signer = TimestampSigner()  # 토큰 만료시간 검증을 위해 signer 불러옴
        token = signer.sign(self.user.pk)  # 사용자 ID를 이용해 서명된 토큰 생성

        url = f"/verify-email/?token={token}"  # url
        response = self.client.get(url)  # get(테스트 이메일인증)

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertEqual(response.json()["message"], "이메일 인증이 완료되었습니다.")  # 메세지

        self.user.refresh_from_db()  # DB에서 사용자 정보 다시 불러오기
        self.assertTrue(self.user.is_active)  # 계정이 활성화되었는지 확인

    def test_login(self):
        url = "/login/"  # 엔드포인트
        data = {"email": "testuser@example.com", "password": "testpassword"}  # 아이디 비밀번호
        response = self.client.post(url, data)  # 로그인 post

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertIn("access", response.cookies)  # access 토큰 값 확인
        self.assertIn("refresh", response.cookies)  # refresh 토큰 값 확인

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)  # 사용자에 대한 JWT refresh 토큰 생성
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")  # 인증 헤더 설정

        url = "/logout/"  # 엔드포인트
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data)  # 로그아웃 post

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)  # 상태 코드 확인
        self.assertEqual(response.json()["message"], "로그아웃 성공.")  # 메세지

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 엔드포인트
        response = self.client.get(url)  # 프로필 get

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertEqual(response.json()["email"], self.user.email)  # 응답 데이터 이메일 확인

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 엔드포인트
        data = {"nickname": "UpdatedNick"}
        response = self.client.patch(url, data)  # 프로필 patch

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.user.refresh_from_db()  # 사용자 데이터 불러오기
        self.assertEqual(self.user.nickname, "UpdatedNick")  # 닉네임 변경 확인

    def test_delete_user_profile(self):
        self.client.force_authenticate(user=self.user)  # 인증된 사용자 설정

        url = "/profile/"  # 엔드포인트
        response = self.client.delete(url)  # 탈퇴 DELETE

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertEqual(response.json()["message"], "회원탈퇴가 완료되었습니다.")  # 메세지
        self.assertFalse(User.objects.filter(email="testuser@example.com").exists())  # 계정 삭제 확인


class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()  # API 클라이언트 생성
        self.user = User.objects.create_user(  # 테스트용 사용자 생성
            email="userreset@example.com", password="testpassword", is_active=True
        )

    def test_request_password_reset(self):
        url = "/password-reset/request/"  # 엔드포인트
        data = {"email": "userreset@example.com"}
        response = self.client.post(url, data)  # 이메일 POST

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertEqual(response.json()["message"], "비밀번호 재설정 링크가 이메일로 전송되었습니다.")  # 메세지

    def test_reset_password(self):
        signer = TimestampSigner()  # 토큰 만료시간 검증을 위해 signer 불러옴
        token = signer.sign(self.user.pk)  # 사용자 ID를 이용해 서명된 토큰 생성

        url = "/password-reset/reset/"  # 엔드포인트
        data = {"token": token, "password": "newpassword"}
        response = self.client.post(url, data)  # reset post

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
        self.assertEqual(response.json()["message"], "비밀번호가 성공적으로 변경되었습니다.")  # 메세지

        login_url = "/login/"  # 엔드포인트
        login_data = {"email": "userreset@example.com", "password": "newpassword"}
        login_response = self.client.post(login_url, login_data)  # 로그인 post

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)  # 상태 코드 확인
