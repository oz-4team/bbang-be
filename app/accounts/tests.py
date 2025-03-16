from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from app.accounts.models import UserImage

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.image_1 = UserImage.objects.create(  # 이미지 1 생성
            image_name="Image One",
            image_url="http://example.com/image1.jpg",
            image_type="jpg"
        )
        self.image_2 = UserImage.objects.create(  # 이미지 2 생성
            image_name="Image Two",
            image_url="http://example.com/image2.jpg",
            image_type="jpg"
        )

    def test_userimage_str(self):
        image_with_name = UserImage.objects.create(  # 이름있는 이미지 생성
            image_name="My Custom Image",
            image_url="http://example.com/custom.jpg",
            image_type="png"
        )
        self.assertEqual(str(image_with_name), "My Custom Image")

        image_without_name = UserImage.objects.create(  # 이름없는 이미지 생성
            image_name=None,
            image_url="http://example.com/default.jpg",
            image_type="jpg"
        )
        self.assertEqual(str(image_without_name), "기본 이미지")  # 이름이 없을 때 기본 이미지로 반환되는지 테스트

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError) as ctx:
            User.objects.create_user(email=None, password="pass123")  # 이메일이 없을경우 메세지, 상태코드 반환 테스트
        self.assertIn("이메일은 필수입니다.", str(ctx.exception))

    def test_create_user_email_normalization(self):
        user = User.objects.create_user(email="Test@Example.COM", password="pass123", nickname="Tester")
        self.assertEqual(user.email, "test@example.com") # 이메일의 정규화(소문자화)가 되는지 테스트

    def test_create_user_and_password_hashing(self):
        password = "pass123"
        user = User.objects.create_user(email="hash@example.com", password=password)  # 비밀번호 해시화 테스트
        self.assertTrue(user.check_password(password))

    def test_create_staffuser(self):
        staff = User.objects.create_staffuser(
            email="staff@example.com", password="staff123", nickname="StaffUser"
        )
        self.assertEqual(staff.email, "staff@example.com") # 스태프 계정을 생성하여 이메일이 맞는지 테스트
        self.assertTrue(staff.is_staff)    # 테스트  staff = True
        self.assertFalse(staff.is_superuser)  # 테스트 superuser = False
        self.assertEqual(str(staff), "StaffUser")  # nickname 테스트

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="admin123", nickname="AdminUser"  # 슈퍼 유저 생성
        )
        self.assertEqual(superuser.email, "admin@example.com")  # 이메일 맞는지 테스트
        self.assertTrue(superuser.is_staff)  # 테스트  staff = True
        self.assertTrue(superuser.is_superuser) # 테스트 superuser = True
        self.assertTrue(superuser.is_active)  # 테스트 is_active = True
        self.assertEqual(str(superuser), "AdminUser") # nickname 테스트

    def test_user_str_method(self):
        user_with_nickname = User.objects.create_user(
            email="nickname@example.com", password="pass123", nickname="Nickname"  # 닉네임 있는 유저 생성
        )
        self.assertEqual(str(user_with_nickname), "Nickname")  # 닉네임 반환 테스트

        user_without_nickname = User.objects.create_user(
            email="noname@example.com", password="pass123", nickname="" # 닉네임 없는 유저 생성
        )
        self.assertEqual(str(user_without_nickname), "noname@example.com")  # 이메일 반환 테스트

    def test_user_image_deletion(self):
        user = User.objects.create_user(
            email="imagetest@example.com",  # 유저 생성해 기본 이미지를 image_id = 1로 연결
            password="pass123",
            nickname="ImageTestUser",
            user_image=self.image_1,
        )
        self.assertEqual(user.user_image, self.image_1)  # 연결 확인

        self.image_1.delete()  # 이미지 삭제
        user.refresh_from_db()  # 데이터베이스 새로고침
        self.assertIsNone(user.user_image)  # 이미지 상태가 None인지 확인