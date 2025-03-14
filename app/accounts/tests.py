from django.contrib.auth import get_user_model
from django.test import TestCase

from app.accounts.models import UserImage

User = get_user_model()


# 유저 모델 테스트
class UserModelTests(TestCase):
    def setUp(self):
        # 기본 이미지 (id=1) 생성
        self.default_image = UserImage.objects.create(
            id=1, image_name="Default Image", image_url="http://example.com/default.jpg", image_type="jpg"
        )
        # 추가 이미지 (id=2) 생성 – 테스트용
        self.another_image = UserImage.objects.create(
            id=2, image_name="example Image", image_url="http://example.com/example.jpg", image_type="png"
        )

    def test_userimage_str(self):
        image_with_name = UserImage.objects.create(
            id=3, image_name="Test Image", image_url="http://example.com/test.jpg", image_type="jpg"  # 이미지 객체 생성
        )
        self.assertEqual(str(image_with_name), "Test Image")  # 이미지 이름이 있을경우 맞는지 확인

        image_without_name = UserImage.objects.create(
            id=4,  # 이미지 객체 생성 이름=None
            image_name=None,
            image_url="http://example.com/noname.jpg",
            image_type="jpg",
        )
        self.assertEqual(str(image_without_name), "기본 이미지")
        # 이미지 이름이 없을경우 기본이미지로 자동변환 되는지 확인

    def test_create_user_without_email(self):
        # 이메일이 없을때 예외처리 작동되는지 확인
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email=None, password="pass123")
        self.assertIn("이메일은 필수입니다.", str(context.exception))

    def test_create_user_email_normalization(self):
        # 이메일 정규화 테스트 email 값이 대소문자 구분없이 들어왔을 경우 소문자화 되는지 확인
        user = User.objects.create_user(email="Test@Example.COM", password="pass123", nickname="Tester")
        self.assertEqual(user.email, "test@example.com")

    def test_create_user_and_password_hashing(self):
        # 비밀번호가 해시화 하여 저장되서 값이 일치한지 확인
        password = "pass123"
        user = User.objects.create_user(email="user@example.com", password=password, nickname="user")
        self.assertTrue(user.check_password(password))

    def test_create_staffuser(self):
        # 스태프 계정 생성하여 권한이 staff=True superuser=False가 맞는지 확인
        staff = User.objects.create_staffuser(email="staff@example.com", password="staff123", nickname="StaffUser")
        self.assertEqual(staff.email, "staff@example.com")
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_superuser)
        # __str__ 메서드는 nickname 반환
        self.assertEqual(str(staff), "StaffUser")

    def test_create_superuser(self):
        # 관리자 계정 생성하여 권한이 다 있는지 확인
        superuser = User.objects.create_superuser(email="admin@example.com", password="admin123", nickname="AdminUser")
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(str(superuser), "AdminUser")

    def test_user_str_method(self):
        # 유저의 닉네임이 있을경우 닉네임, 닉네임이 없을경우 이메일을 반환하는지 확인
        user_with_nickname = User.objects.create_user(
            email="nickname@example.com", password="pass123", nickname="nickname"
        )
        self.assertEqual(str(user_with_nickname), "nickname")
        user_without_nickname = User.objects.create_user(email="noname@example.com", password="pass123", nickname="")
        self.assertEqual(str(user_without_nickname), "noname@example.com")

    def test_user_image_on_delete_set_default(self):
        # 추가 이미지가 적용되어있고 이미지를 삭제했을때 기본이미지를 사용하는지 확인
        user = User.objects.create_user(
            email="testuserimage@example.com", password="pass", nickname="testuser", user_image=self.another_image
        )
        self.assertEqual(user.user_image.id, 2)  # user_image_id = 2
        self.another_image.delete()  # id2번 이미지 삭제
        user.refresh_from_db()
        self.assertEqual(user.user_image.id, 1)
