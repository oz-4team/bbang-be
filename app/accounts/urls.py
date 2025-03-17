from django.urls import path

from app.accounts.views import (
    CheckResetTokenAPIView,
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
    RequestPasswordResetAPIView,
    ResetPasswordAPIView,
    UserProfileAPIView,
    VerifyEmailAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),  # 회원가입 URL 패턴
    path("login/", LoginAPIView.as_view(), name="login"),  # 로그인 URL 패턴
    path("logout/", LogoutAPIView.as_view(), name="logout"),  # 로그아웃 URL 패턴
    path("verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),  # 이메일 인증 URL 패턴
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("password-reset/check-token/", CheckResetTokenAPIView.as_view(), name="check-token"),
    path("password-reset/request/", RequestPasswordResetAPIView.as_view(), name="password-reset1"),
    path("password-reset/reset/", ResetPasswordAPIView.as_view(), name="password-reset2"),
]
