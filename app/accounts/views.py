from django.contrib.auth import get_user_model
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from app.accounts.email import send_password_reset_email
from app.accounts.serializers import ProfileSerializer, RegisterSerializer

User = get_user_model()


# 회원가입 API
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def post(self, request):  # POST
        serializer = RegisterSerializer(data=request.data)  # 요청 데이터를 RegisterSerializer에 삽입
        if serializer.is_valid():  # 입력 데이터 유효성 검사
            serializer.save()  # 유효할 경우 사용자 생성 및 이메일 인증 메일 전송
            return Response(
                {"message": "회원가입 성공. 이메일 인증을 위해 메일을 확인해주세요."},  # 메세지
                status=status.HTTP_201_CREATED,  # 상태코드
            )
        return Response(
            serializer.errors,  # 유효하지 않을 경우 에러와 상태 코드 반환
            status=status.HTTP_400_BAD_REQUEST,
        )


# 이메일 인증API
class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def get(self, request):  # 이메일 인증
        token = request.GET.get("token")  # URL 쿼리 파라미터에서 "token" 값을 추출
        if not token:  # 토큰이 제공되지 않은 경우
            return Response(
                {"error": "토큰이 제공되지 않았습니다."},  # 메세지
                status=status.HTTP_400_BAD_REQUEST,  # 상태코드
            )

        signer = TimestampSigner()  # 토큰의 서명과 만료를 검증하기 위한 TimestampSigner 인스턴스 생성
        try:
            # 토큰의 서명을 검증하며, 최대 1시간(초단위) 동안만 유효한 것으로 체크
            user_pk = signer.unsign(token, max_age=3600)  # 토큰에서 사용자 pk 추출
            user = User.objects.get(pk=user_pk)  # pk로 사용자 조회해 user에 저장
            user.is_active = True  # 사용자의 이메일 인증 상태를 True로 변경 (인증 완료)
            user.save()  # 데이터베이스 저장
            return Response(
                {"message": "이메일 인증이 완료되었습니다."},  # 메세지
                status=status.HTTP_200_OK,  # 상태코드
            )
        except SignatureExpired:  # 만약 토큰이 만료된 경우
            try:
                user_pk = signer.unsign(token, max_age=None)  # 시간 검증 생략 후 사용자 pk추출
                user = User.objects.get(pk=user_pk)  # pk로 사용자 조회해 user에 저장
                user.delete()  # 이메일 인증 토큰이 만료 되었기에 계정 삭제처리
                return Response(
                    {"error": "토큰이 만료되어 계정이 삭제되었습니다."},  # 메세지
                    status=status.HTTP_400_BAD_REQUEST,  # 상태코드
                )
            except Exception as inner_error:  # 토큰 삭제시 오류 발생하면
                return Response(
                    {"error": "토큰 만료로 인한 계정 삭제 과정에서 오류가 발생하였습니다."},  # 메세지
                    status=status.HTTP_400_BAD_REQUEST,  # 상태코드
                )
        except BadSignature:  # 토큰이 일치하지 않으면
            return Response(
                {"error": "유효하지 않은 토큰입니다."},  # 메세지
                status=status.HTTP_400_BAD_REQUEST,  # 상태코드
            )


# 로그인 API
class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def post(self, request, *args, **kwargs):  # POST
        response = super().post(request, *args, **kwargs)  # JWT 토큰 발급(부모 클래스에서)
        if response.status_code == 200:  # 토큰 발급 성공 시
            tokens = response.data  # 발급된 토큰 데이터를 변수에 저장
            user = User.objects.get(email=request.data['email'])  # 로그인 요청 데이터에서 이메일을 통해 사용자 조회
            response.set_cookie(  # 쿠키 설정
                key="access",  # access 쿠키 이름
                value=tokens["access"],  # 토큰 값 저장 (access)
                httponly=True,  # 스크립트에서 쿠키에 직접 접근을 막아 xss 공격 방어 도움
                secure=True,  # HTTPS 환경에서만 쿠키 전송
                samesite="Lax",  # CSRF 보호, 외부 링크 또는 일부 GET요청에도 쿠키 전송 가능
            )
            response.set_cookie(
                key="refresh",  # refresh 쿠키 이름
                value=tokens["refresh"],  # 토큰 값 저장 (refresh)
                httponly=True,
                samesite="Lax",
            )
            # 사용자 정보 추가
            response.data.update({
                "email": user.email,  # 사용자 이메일 추가
                "nickname": user.nickname,  # 사용자 닉네임 추가
                "is_staff": user.is_staff,  # 관리자 여부 추가
                "image": user.user_image.image.url if user.user_image and user.user_image.image else None
            })
        return response  # 최종 응답 반환


# 로그아웃 API
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근가능

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]  # 클라이언트로부터 받은 토큰 추출
            print("전달받은 토큰:", refresh_token)  # 전달받은 토큰 값 로그 출력 (디버깅 용도)
            token = RefreshToken(refresh_token)  # 타입확인, 구조확인 검사
            token.blacklist()
            # TokenBlacklisting 기능으로 블랙리스트 DB에 저장해 다시 인증을 거부
            return Response({"message": "로그아웃 성공."}, status=status.HTTP_205_RESET_CONTENT)  # 메세지 상태코드
        except Exception as e:
            print("로그아웃 중 오류 발생.:", e)  # 오류 로그
            return Response(
                {"error": "오류가 발생했습니다. 전달받은 토큰을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )  # 메세지 상태코드


# 사용자 조회, 변경, 탈퇴 API
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근가능

    def get_object(self):
        return self.request.user  # 사용자 객체를 가져오기

    def get(self, request, *args, **kwargs):  # GET
        user = self.get_object()  # get_object 가져오기
        serializer = ProfileSerializer(user)  # 사용자 객체를 직렬화 -> JSON 형식으로 변환
        return Response(serializer.data, status=status.HTTP_200_OK)  # 변환된 값과 상태코드 출력

    def patch(self, request, *args, **kwargs):  # PATCH.
        user = self.get_object()  # 현재 사용자 가져오기
        data = request.data.copy()  # 요청 데이터를 복사하여 수정 가능하도록 함

        # 만약 요청 데이터에 "password" 필드가 포함되어 있다면
        if "password" in data:  # 비밀번호 재설정시 해시화
            user.set_password(data["password"])  # 비밀번호 해시화 적용
            user.save()  # 변경된 비밀번호 저장
            return Response(
                {"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK
            )  # 응답 반환

        serializer = ProfileSerializer(user, data=data, partial=True)  # 일반적인 사용자 정보 업데이트
        if serializer.is_valid():  # 데이터 유효성 검사
            serializer.save()  # 변경사항 저장
            return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터 응답 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효하지 않으면 오류 반환

    def delete(self, request, *args, **kwargs):  # DELETE
        user = self.get_object()  # get_object 가져오기
        user.delete()  # 사용자 객체 삭제
        return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)


# 사용자 비밀번호 재설정 메일 전송 API
class RequestPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def post(self, request):
        email = request.data.get("email")  # 요청에서 이메일을 가져옴
        if not email:
            return Response(
                {"error": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )  # 이메일이 없을 경우 오류 반환

        try:
            user = User.objects.get(
                email=email.strip()
            )  # 해당 이메일을 가진 사용자 조회 strip()을 사용해 앞뒤 공백 삭제
        except User.DoesNotExist:
            return Response(
                {"error": "해당 이메일을 가진 사용자가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        send_password_reset_email(user)  # 비밀번호 재설정 이메일 전송 함수

        return Response({"message": "비밀번호 재설정 링크가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)


# 사용자 비밀번호 재설정 토큰검증 API
class CheckResetTokenAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get(self, request):
        token = request.GET.get("token")  # URL에서 토큰 가져오기
        if not token:
            return Response({"error": "토큰이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(token, max_age=3600)  # 토큰 검증 (1시간 이내 유효)  이메일인증 만료시간
            user = User.objects.get(pk=user_pk)  # 사용자 조회
            return Response({"message": "토큰이 유효합니다.", "user_id": user.id}, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"error": "토큰이 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 사용자 비밀번호 재설정 API
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def post(self, request):
        token = request.data.get("token")  # 요청에서 토큰을 가져옴
        new_password = request.data.get("password")  # 요청에서 새로운 비밀번호를 가져옴

        if not token or not new_password:
            return Response(
                {"error": "토큰과 새 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )  # 필수 데이터 누락 시 오류 반환

        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(token, max_age=3600)  # 토큰 검증 (1시간 이내 유효)  이메일인증 만료시간
            user = User.objects.get(pk=user_pk)  # 사용자 조회
            user.set_password(new_password)  # 새 비밀번호를 해시화하여 저장
            user.save()
            return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"error": "토큰이 만료되었습니다. 다시 요청해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
