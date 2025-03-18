from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from app.accounts.models import UserImage

# 현재 프로젝트에서 사용하는 User 모델 객체를 가져옴
User = get_user_model()


class GoogleOAuth2LoginView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근할 수 있도록 설정

    def get(self, request):
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"  # 구글 로그인 페이지로 리다이렉트

        # 구글에 전송할 파라미터 설정
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,  # 클라이언트 아이디
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,  # 콜백 URL
            "response_type": "code",
            "scope": "openid email profile",  # 가져올 정보 범위
            "access_type": "offline",
        }

        url = f"{google_auth_url}?{urlencode(params)}"  # 파라미터를 인코딩해 url 생성

        return redirect(url)  # 생성한 url로 리다이렉트


class GoogleOAuth2CallbackView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def get(self, request):
        code = request.GET.get("code")  # Authorization Code 가져옴
        if not code:
            # code가 없는 경우 오류 반환
            return HttpResponseBadRequest("authorization code가 존재하지 않습니다.")  # 코드가 없을경우 예외처리

        token_url = "https://oauth2.googleapis.com/token"  # post요청으로 AccessToken 받아옴
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,  # 클라이언트 ID
            "client_secret": settings.GOOGLE_CLIENT_SECRET,  # 클라이언트 시크릿
            "code": code,  # Authorization Code
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,  # 콜백 URL
            "grant_type": "authorization_code",  # OAuth2 표준 (Authorization Code Grant)
        }
        token_response = requests.post(token_url, data=data)
        token_data = token_response.json()

        access_token = token_data.get("access_token")  # Access Token 추출
        if not access_token:
            return HttpResponseBadRequest("토큰이 유효하지 않습니다.")  # 토큰이 없으면 예외처리

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"  # 발급받은 Access Token으로 사용자 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()

        email = userinfo.get("email")  # 구글 이메일
        if not email:
            return HttpResponseBadRequest("구글에서 사용자 이메일을 검색하지 못했습니다.")  # 이메일이 없으면 예외처리

        # 필요한 정보들 받기
        nickname_from_google = userinfo.get("given_name")  # 이름
        gender_from_google = userinfo.get("gender")  # 성별
        picture_url = userinfo.get("picture")  # 프로필 이미지

        defaults = {
            "is_active": True,  # 새로 생성 시 계정을 즉시 활성화
        }
        if nickname_from_google:  # 닉네임 있을경우 defaults에 저장
            defaults["nickname"] = nickname_from_google
        if gender_from_google:  # 성별 있을경우 defaults에 저장
            defaults["gender"] = gender_from_google

        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        # 이메일을 기준으로 데이터베이스에 없으면 회원가입, 있으면 로그인

        if picture_url:
            if user.user_image:  # 만약 프로필 이미지가 존재하면 이미지를 가져와 저장
                user.user_image.image_url = picture_url
                user.user_image.image_name = f"{nickname_from_google or 'google_user'}_img"
                user.user_image.image_type = "GoogleProfile"
                user.user_image.save()
            else:
                if not picture_url:  # 프로필 이미지가 없으면 기본 이미지를 가져옴
                    picture_url = "https://example.com/default_profile.png"

                user_image = UserImage.objects.create(  # 가져온 이미지를 토대로 데이터베이스에 저장
                    image_url=picture_url,
                    image_name=f"{nickname_from_google or 'google_user'}_img",
                    image_type="GoogleProfile",
                )
                user.user_image = user_image
                user.save()

        if not created:  # 이미 존재하는 사용자일 경우
            changed = False

            # is_active가 False라면 True로 설정
            if not user.is_active:
                user.is_active = True
                changed = True

            # 닉네임이 없는 경우, 구글 닉네임으로 저장
            if not user.nickname and nickname_from_google:
                user.nickname = nickname_from_google
                changed = True

            # 성별이 없는 경우, 구글 성별로 저장
            if not user.gender and gender_from_google:
                user.gender = gender_from_google
                changed = True

            # 변경 사항이 있다면 DB에 저장
            if changed:
                user.save()

        return JsonResponse(  # 사용자 반환
            {
                "message": "구글 로그인 성공",  # 상태 메시지
                "created_new_user": created,  # True면 새 계정 생성, False면 기존 계정
                "email": user.email,  # 사용자 이메일
                "nickname": user.nickname,  # 사용자 닉네임
                "gender": user.gender,  # 사용자 성별
                "image_url": user.user_image.image_url if user.user_image else None,
            }
        )


class KakaoOAuth2LoginView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def get(self, request):
        kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"  # 카카오 인증 페이지
        # 카카오에 전달할 파라미터
        params = {
            "client_id": settings.KAKAO_CLIENT_ID,  # 카카오 REST API 키
            "redirect_uri": settings.KAKAO_REDIRECT_URI,  # 콜백 URL
            "response_type": "code",  # Authorization Code 발급
            "scope": "profile_nickname profile_image account_email gender",
        }

        url = f"{kakao_auth_url}?{urlencode(params)}"  # 파라미터를 인코딩해 url생성
        return redirect(url)  # 생성한 url로 리다이렉트


class KakaoOAuth2CallbackView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def get(self, request):
        code = request.GET.get("code")  # 코드 가져옴
        if not code:
            return HttpResponseBadRequest("카카오로부터 code가 전달되지 않았습니다.")  # 코드 없을경우 예외처리

        token_url = "https://kauth.kakao.com/oauth/token"  # post요청으로 AccessToken 받아옴
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,  # 클라이언트 ID
            "redirect_uri": settings.KAKAO_REDIRECT_URI,  # 롤백 url
            "code": code,  # Authorization Code
        }
        token_response = requests.post(token_url, data=data)
        token_json = token_response.json()

        # 만약 에러가 있다면 처리
        error_description = token_json.get("error_description")
        if error_description:
            return HttpResponseBadRequest(f"카카오 인증 실패: {error_description}")

        access_token = token_json.get("access_token")  # Access_token 추출
        if not access_token:
            return HttpResponseBadRequest("Access Token이 존재하지 않습니다.")  # Access token 없을경우 예외처리

        userinfo_url = "https://kapi.kakao.com/v2/user/me"  # 발급받은 Access token으로 사용자 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.post(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()

        kakao_account = userinfo.get("kakao_account", {})  # 카카오 계정 정보 및 프로필 정보
        profile_info = kakao_account.get("profile", {})

        # 필요한 정보 받기
        email = kakao_account.get("email")  # 이메일
        nickname = profile_info.get("nickname")  # 닉네임
        gender = kakao_account.get("gender")  # 성별
        picture_url = profile_info.get("profile_image_url")  # 프로필 이미지

        defaults = {
            "is_active": True,  # 가입 즉시 활성화
        }
        if nickname:
            defaults["nickname"] = nickname  # 닉네임 있을경우 defaults에 저장
        if gender:
            defaults["gender"] = gender  # 성별 있을경우 defaults에 저장

        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        # 이메일을 기준으로 데이터베이스에 없으면 회원가입, 있으면 로그인

        if picture_url:
            if user.user_image:  # 만약 프로필 이미지가 존재하면 이미지를 가져옴
                user.user_image.image_url = picture_url
                user.user_image.image_name = f"{nickname or 'kakao_user'}_img"
                user.user_image.image_type = "KakaoProfile"
                user.user_image.save()
            else:
                # 가져온 이미지를 통해 데이터베이스에 저장
                user_image = UserImage.objects.create(
                    image_url=picture_url,
                    image_name=f"{nickname or 'kakao_user'}_img",
                    image_type="KakaoProfile",
                )
                user.user_image = user_image
                user.save()

        if not created:  # 이미 존재하는 사용자일 경우
            changed = False
            if not user.is_active:  # is_active가 False라면 True로 변경하고 changed를 True로
                user.is_active = True
                changed = True
            if not user.nickname and nickname:  # nickname 없으면 이름을 저장하고 changed를 True로
                user.nickname = nickname
                changed = True
            if not user.gender and gender:  # gender 없으면 성별을 저장하고 changed를 True로
                user.gender = gender
                changed = True
            if changed:  # 변경사항이 있다면 DB에 저장
                user.save()

        return JsonResponse(  # 사용자 반환
            {
                "message": "카카오 로그인 성공",
                "created_new_user": created,
                "email": user.email,
                "nickname": user.nickname,
                "gender": user.gender,
                "image_url": user.user_image.image_url if user.user_image else None,
            }
        )


class NaverOAuth2LoginView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def get(self, request):
        naver_auth_url = "https://nid.naver.com/oauth2.0/authorize"  # 네이버 인증 페이지

        # 네이버에 전달할 파라미터
        params = {
            "response_type": "code",  # Authorization Code 발급
            "client_id": settings.NAVER_CLIENT_ID,  # 네이버 REST API 아이디
            "redirect_uri": settings.NAVER_REDIRECT_URI,  # 콜백 URL
            "state": "random_state_string",
        }

        url = f"{naver_auth_url}?{urlencode(params)}"  # 파라미터를 인코딩해 url생성

        return redirect(url)  # 생성한 url로 리다이렉트


class NaverOAuth2CallbackView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 허용

    def get(self, request):
        code = request.GET.get("code")  # Authorization Code  가져옴
        state = request.GET.get("state")  # 위변조 방지용 state (인증 시에 같이 보냄)
        if not code:
            return HttpResponseBadRequest("네이버로부터 code가 전달되지 않았습니다.")  # 코드가 없을경우 예외처리

        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",  # Authorization Code
            "client_id": settings.NAVER_CLIENT_ID,  # 클라이언트 아이디
            "client_secret": settings.NAVER_CLIENT_SECRET,  # 클라이언트 시크릿
            "code": code,  # Authorization Code
            "state": state,  # 위변조 방지용 state
        }
        token_response = requests.post(token_url, data=data)  # post요청으로 AccessToken 받아옴
        token_json = token_response.json()

        # 에러 처리
        error = token_json.get("error")
        if error:
            return HttpResponseBadRequest(f"네이버 인증 실패: {token_json.get('error_description')}")

        access_token = token_json.get("access_token")  # Access token 추출
        if not access_token:  # 토큰이 없으면 예외처리
            return HttpResponseBadRequest("네이버 Access Token이 존재하지 않습니다.")

        userinfo_url = "https://openapi.naver.com/v1/nid/me"  # 발급받은 Access Token으로 사용자 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()

        if userinfo.get("resultcode") != "00":  # 결과코드가 00이 아닐경우 예외처리
            return HttpResponseBadRequest("네이버 사용자 정보를 가져오지 못했습니다.")

        # 필요한 정보 받기
        response_data = userinfo.get("response", {})
        email = response_data.get("email")  # "user@naver.com"
        nickname = response_data.get("nickname")  # "홍길동"
        profile_image = response_data.get("profile_image")  # 네이버 프로필 이미지 URL
        gender = response_data.get("gender")  # "M" or "F" (동의 항목에 따라)

        if not email:  # 이메일이 없으면 예외처리
            return HttpResponseBadRequest("네이버에서 이메일을 전달받지 못했습니다.")

        defaults = {
            "is_active": True,  # 즉시 활성화
        }
        if nickname:  # 닉네임 defaults에 저장
            defaults["nickname"] = nickname
        if gender:  # 성별 저장
            if gender == "M":
                gender = "male"
            elif gender == "F":
                gender = "female"
            else:
                gender = None
            defaults["gender"] = gender

        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        # 이메일을 기준으로 데이터베이스에 없으면 회원가입, 있으면 로그인

        if profile_image:
            if user.user_image:  # 만약 프로필 이미지가 존재하면 이미지를 가져와 저장
                user.user_image.image_url = profile_image
                user.user_image.image_name = f"{nickname or 'naver_user'}_img"
                user.user_image.image_type = "NaverProfile"
                user.user_image.save()
            else:  # 없으면 기본 이미지 저장
                user_image = UserImage.objects.create(
                    image_url=profile_image,
                    image_name=f"{nickname or 'naver_user'}_img",
                    image_type="NaverProfile",
                )
                user.user_image = user_image
                user.save()

        if not created:  # 이미 존재하는 사용자일 경우
            changed = False
            if not user.is_active:  # is_active가 False라면 True로 변경하고 changed를 True로
                user.is_active = True
                changed = True
            if not user.nickname and nickname:  # nickname 없으면 이름을 저장하고 changed를 True로
                user.nickname = nickname
                changed = True
            if not user.gender and gender:  # gender 없으면 성별을 저장하고 changed를 True로
                user.gender = gender
                changed = True
            if changed:  # 변경사항이 있다면 DB에 저장
                user.save()

        # 사용자 반환
        return JsonResponse(
            {
                "message": "네이버 로그인 성공",
                "created_new_user": created,
                "email": user.email,
                "nickname": user.nickname,
                "gender": user.gender,
                "image_url": user.user_image.image_url if user.user_image else None,
            }
        )
