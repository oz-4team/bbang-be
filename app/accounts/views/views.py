import logging

from django.contrib.auth import get_user_model
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from app.accounts.email import send_password_reset_email
from app.accounts.serializers import ProfileSerializer, RegisterSerializer

User = get_user_model()
account_error = logging.getLogger("account")

# # log test
# def cause_zero_division_error():
#     try:
#         return 1 / 0
#     except Exception as e:
#         account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
#         return Response(
#             {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#
# cause_zero_division_error()


# 회원가입 API
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="이메일, 비밀번호, 닉네임 등을 받아 새로운 사용자를 생성하고 이메일 인증 메일을 전송.",
        request_body=RegisterSerializer,  # 요청 바디로 받을 시리얼라이저 지정
        responses={
            201: openapi.Response(
                description="회원가입 성공",
                examples={"application/json": {"message": "회원가입 성공. 이메일 인증을 위해 메일을 확인해주세요."}},
            ),
            400: "잘못된 요청 또는 유효성 검증 실패",
            500: "서버 오류",
        },
    )
    def post(self, request):  # POST
        try:
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
        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 이메일 인증API
class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    @swagger_auto_schema(
        operation_summary="이메일 인증",
        operation_description="이메일로 전송된 토큰을 GET 파라미터로 받아서 이메일 인증 완료.",
        manual_parameters=[
            openapi.Parameter(
                name="token",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="이메일 인증 토큰",
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="인증 완료",
                examples={"application/json": {"message": "이메일 인증이 완료되었습니다."}},
            ),
            400: "토큰이 없거나 유효하지 않은 경우",
            500: "서버 오류",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="이메일과 비밀번호를 받아 JWT 토큰을 발급",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="사용자 이메일"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="비밀번호"),
            },
            required=["email", "password"],
        ),
        responses={
            200: openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "refresh": "<refresh_token>",
                        "access": "<access_token>",
                        "id": 1,
                        "email": "test@example.com",
                        "nickname": "test",
                        "is_staff": False,
                        "image_url": "http://example.com/profile_images/test.jpg",
                    }
                },
            ),
            400: "이메일 혹은 비밀번호 미전달",
            404: "존재하지 않는 사용자",
            500: "서버 오류",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                tokens = response.data
                try:
                    email = request.data["email"]  # KeyError 발생 가능
                except KeyError:
                    return Response({"error": "이메일이 전달되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    user = User.objects.get(email=email)  # DoesNotExist 발생 가능
                except User.DoesNotExist:
                    return Response(
                        {"error": "해당 이메일을 가진 사용자가 존재하지 않습니다."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                response.set_cookie(
                    key="access",
                    value=tokens["access"],
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                )
                response.set_cookie(
                    key="refresh",
                    value=tokens["refresh"],
                    httponly=True,
                    samesite="Lax",
                )
                response.data.update(
                    {
                        "id": user.id,
                        "email": user.email,
                        "nickname": user.nickname,
                        "is_staff": user.is_staff,
                        "image_url": user.image_url.url if user.image_url else None,
                    }
                )
            return response

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 로그아웃 API
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근가능

    @swagger_auto_schema(
        operation_summary="로그아웃",
        operation_description="Refresh 토큰을 받아 해당 토큰을 블랙리스트 처리",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh 토큰"),
            },
            required=["refresh"],
        ),
        responses={
            205: openapi.Response(
                description="로그아웃 성공",
                examples={"application/json": {"message": "로그아웃 성공."}},
            ),
            400: "토큰이 없거나 유효하지 않은 경우",
            500: "서버 오류",
        },
    )
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
        try:
            return self.request.user  # 사용자 객체를 가져오기
        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="사용자 정보 조회",
        operation_description="로그인된 사용자의 정보를 조회합니다.",
        responses={
            200: openapi.Response(
                description="조회 성공",
                examples={
                    "application/json": {
                        "email": "test@example.com",
                        "nickname": "테스터",
                        "gender": "male",
                        "age": 25,
                        "image_url": "http://example.com/profile_images/test.jpg",
                    }
                },
            ),
            500: "서버 오류",
        },
    )
    def get(self, request, *args, **kwargs):  # GET
        try:
            user = self.get_object()  # get_object 가져오기
            serializer = ProfileSerializer(user)  # 사용자 객체를 직렬화 -> JSON 형식으로 변환
            return Response(serializer.data, status=status.HTTP_200_OK)  # 변환된 값과 상태코드 출력

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="사용자 정보 수정",
        operation_description="로그인된 사용자의 닉네임, 비밀번호, 프로필 이미지 등을 수정",
        request_body=ProfileSerializer,
        responses={
            200: openapi.Response(
                description="수정 성공",
                examples={
                    "application/json": {
                        "email": "test@example.com",
                        "nickname": "변경된닉네임",
                        "gender": "female",
                        "age": 30,
                        "image_url": "http://example.com/profile_images/test_new.jpg",
                    }
                },
            ),
            400: "요청 데이터가 유효하지 않음",
            500: "서버 오류",
        },
    )
    def patch(self, request, *args, **kwargs):  # PATCH.
        try:
            user = self.get_object()  # 현재 사용자 가져오기
            data = request.data.copy()  # 요청 데이터를 복사하여 수정 가능하도록 함

            if "current_password" not in data: # 현재비밀번호 입력한지 검증
                return Response(
                    {"error": "현재 비밀번호를 입력해야 합니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if "current_password" in data: # 입력한 비밀번호와 유저의 비밀번호 검증
                current_password = data["current_password"]

                # 사용자의 실제 비밀번호 확인 (일반적으로 user.password는 해시된 값)
                if not user.check_password(current_password):
                    return Response(
                        {"error": "현재 비밀번호가 올바르지 않습니다."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = ProfileSerializer(user, data=data, partial=True)  # 일반적인 사용자 정보 업데이트
            if serializer.is_valid():  # 데이터 유효성 검사
                serializer.save()  # 변경사항 저장
                return Response(serializer.data, status=status.HTTP_200_OK)  # 수정된 데이터 응답 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효하지 않으면 오류 반환

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="회원 탈퇴",
        operation_description="로그인된 사용자 계정삭제",
        responses={
            200: openapi.Response(
                description="탈퇴 성공",
                examples={"application/json": {"message": "회원탈퇴가 완료되었습니다."}},
            ),
            500: "서버 오류",
        },
    )
    def delete(self, request, *args, **kwargs):  # DELETE
        try:
            user = self.get_object()  # get_object 가져오기
            user.delete()  # 사용자 객체 삭제
            return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 사용자 비밀번호 재설정 메일 전송 API
class RequestPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 이메일전송",
        operation_description="이메일을 받아 해당 사용자에게 비밀번호 재설정 링크전송",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="사용자 이메일"),
            },
            required=["email"],
        ),
        responses={
            200: openapi.Response(
                description="메일 전송 성공",
                examples={"application/json": {"message": "비밀번호 재설정 링크가 이메일로 전송되었습니다."}},
            ),
            400: "이메일 미전달",
            404: "해당 이메일의 사용자가 없음",
            500: "서버 오류",
        },
    )
    def post(self, request):
        try:
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

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 사용자 비밀번호 재설정 토큰검증 API
class CheckResetTokenAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @swagger_auto_schema(
        operation_summary="비밀번호 재설정 토큰 검증",
        operation_description="이메일로 전송된 토큰의 유효성검사",
        manual_parameters=[
            openapi.Parameter(
                name="token",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="비밀번호 재설정용 토큰",
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="토큰 유효",
                examples={"application/json": {"message": "토큰이 유효합니다.", "user_id": 1}},
            ),
            400: "토큰이 없거나 만료/유효하지 않음",
            404: "사용자 없음",
            500: "서버 오류",
        },
    )
    def get(self, request):
        try:
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

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 사용자 비밀번호 재설정 API
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @swagger_auto_schema(
        operation_summary="비밀번호 재설정",
        operation_description="토큰과 새 비밀번호를 받아 실제 비밀번호변경",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "token": openapi.Schema(type=openapi.TYPE_STRING, description="비밀번호 재설정용 토큰"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="새로운 비밀번호"),
            },
            required=["token", "password"],
        ),
        responses={
            200: openapi.Response(
                description="비밀번호 변경 성공",
                examples={"application/json": {"message": "비밀번호가 성공적으로 변경되었습니다."}},
            ),
            400: "토큰/비밀번호 누락, 토큰 만료, 토큰 위조 등",
            404: "사용자 없음",
            500: "서버 오류",
        },
    )
    def post(self, request):
        try:
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
                return Response(
                    {"error": "토큰이 만료되었습니다. 다시 요청해주세요."}, status=status.HTTP_400_BAD_REQUEST
                )
            except BadSignature:
                return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            account_error.error(f"Account API 에러 발생 {e}", exc_info=True)  # Error exc_info 예외발생위치 저장
            return Response(
                {"message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
