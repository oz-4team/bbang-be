from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError) as ctx:
            User.objects.create_user(email=None, password="pass123")
        self.assertIn("이메일은 필수입니다.", str(ctx.exception))

    def test_create_user_email_normalization(self):
        user = User.objects.create_user(email="Test@Example.COM", password="pass123", nickname="Tester")
        self.assertEqual(user.email, "test@example.com")

    def test_create_user_and_password_hashing(self):
        password = "pass123"
        user = User.objects.create_user(email="hash@example.com", password=password)
        self.assertTrue(user.check_password(password))

    def test_create_staffuser(self):
        staff = User.objects.create_staffuser(email="staff@example.com", password="staff123", nickname="StaffUser")
        self.assertEqual(staff.email, "staff@example.com")
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_superuser)
        self.assertEqual(str(staff), "StaffUser")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="admin123", nickname="AdminUser"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(str(superuser), "AdminUser")

    def test_user_str_method(self):
        user_with_nickname = User.objects.create_user(
            email="nickname@example.com", password="pass123", nickname="Nickname"
        )
        self.assertEqual(str(user_with_nickname), "Nickname")

        user_without_nickname = User.objects.create_user(
            email="noname@example.com", password="pass123", nickname=""
        )
        self.assertEqual(str(user_without_nickname), "noname@example.com")

    def test_default_image_url(self):
        # 사용자가 이미지 URL을 지정하지 않으면 기본 이미지 경로가 할당되어야 합니다.
        user = User.objects.create_user(
            email="defaultimage@example.com", password="pass123", nickname="DefaultImageUser"
        )
        self.assertEqual(user.image_url, "profile_images/default_profile_image.jpg")