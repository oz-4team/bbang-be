import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# from app.accounts.models import UserImage  # 더 이상 사용하지 않음

# 현재 프로젝트에서 사용하는 User 모델 객체를 가져옴
User = get_user_model()
account_error = logging.getLogger("account")


class GoogleOAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            code = request.data.get("code")
            if not code:
                return HttpResponseBadRequest("인가 코드가 전달되지 않았습니다.")

            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            token_response = requests.post(
                token_url, data=data, headers={"content-type": "application/x-www-form-urlencoded"}
            )
            if token_response.status_code != 200:
                error_text = token_response.text
                return HttpResponseBadRequest(f"토큰요청실패: {error_text}")

            access_token = token_response.json().get("access_token")
            if not access_token:
                return HttpResponseBadRequest("액세스 토큰을 발급받지 못했습니다.")

            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            email = userinfo_response.get("email")
            nickname = userinfo_response.get("given_name")
            if not nickname and email:
                nickname = email.split("@")[0]
            picture_url = userinfo_response.get("picture")
            gender = userinfo_response.get("gender", None)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "nickname": nickname,
                    "gender": gender,
                    "is_active": True,
                },
            )

            if picture_url:
                user.image_url = picture_url
                user.save()

            refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "message": "구글 로그인 성공",
                    "created_new_user": created,
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "gender": user.gender,
                    "image_url": str(user.image_url),
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "is_staff": user.is_staff,
                }
            )

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class KakaoOAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            code = request.data.get("code")
            if not code:
                return HttpResponseBadRequest("인가 코드가 전달되지 않았습니다.")

            token_url = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            }
            token_response = requests.post(token_url, data=data).json()

            print("Kakao Token Response:", token_response)

            access_token = token_response.get("access_token")
            if not access_token:
                error_desc = token_response.get("error_description", "액세스 토큰 발급 실패 (이유 미제공)")
                return HttpResponseBadRequest(f"액세스 토큰을 발급받지 못했습니다. 사유: {error_desc}")

            userinfo_response = requests.get(
                "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            print("Kakao UserInfo Response:", userinfo_response)

            kakao_account = userinfo_response.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            email = kakao_account.get("email")
            nickname = profile.get("nickname")
            picture_url = profile.get("profile_image_url")
            gender = kakao_account.get("gender")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "nickname": nickname,
                    "gender": gender,
                    "is_active": True,
                },
            )

            if picture_url:
                user.image_url = picture_url
                user.save()

            refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "message": "카카오 로그인 성공",
                    "created_new_user": created,
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "gender": user.gender,
                    "image_url": str(user.image_url),
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "is_staff": user.is_staff,
                }
            )

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NaverOAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            code = request.data.get("code")
            state = request.data.get("state")
            if not code or not state:
                return HttpResponseBadRequest("인가 코드 또는 상태값이 전달되지 않았습니다.")

            token_url = "https://nid.naver.com/oauth2.0/token"
            data = {
                "grant_type": "authorization_code",
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
                "code": code,
                "state": state,
            }
            token_response = requests.post(token_url, data=data)
            if token_response.status_code != 200:
                return HttpResponseBadRequest(f"{token_response.error_description}")

            access_token = token_response.json().get("access_token")
            if not access_token:
                return HttpResponseBadRequest("액세스 토큰을 발급받지 못했습니다.")

            userinfo_response = requests.get(
                "https://openapi.naver.com/v1/nid/me", headers={"Authorization": f"Bearer {access_token}"}
            )
            if userinfo_response.status_code != 200:
                return HttpResponseBadRequest(f"{userinfo.error_description}")

            response_data = userinfo_response.json().get("response", {})
            email = response_data.get("email")
            nickname = response_data.get("nickname")
            picture_url = response_data.get("profile_image")
            gender = response_data.get("gender")
            gender = "male" if gender == "M" else "female" if gender == "F" else None

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "nickname": nickname,
                    "gender": gender,
                    "is_active": True,
                },
            )

            if picture_url:
                user.image_url = picture_url
                user.save()

            refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "message": "네이버 로그인 성공",
                    "created_new_user": created,
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "gender": user.gender,
                    "image_url": str(user.image_url),
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "is_staff": user.is_staff,
                }
            )

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
