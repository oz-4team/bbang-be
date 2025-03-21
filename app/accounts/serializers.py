from django.contrib.auth import get_user_model  # 현재 프로젝트의 사용자 모델을 가져옴
from rest_framework import serializers  # DRF 직렬화 기능을 사용하기 위한 모듈 임포트
from drf_extra_fields.fields import Base64ImageField  # base64 인코딩 이미지를 처리하기 위한 필드

from app.accounts.email import send_verification_email  # 이메일 전송 함수 임포트

User = get_user_model()  # User 모델 할당


# 회원가입 Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 비밀번호는 쓰기 전용으로 설정
    # 프론트엔드에서 base64 인코딩된 이미지를 "image" 키로 전달하면 처리함
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User  # CustomUser 모델 (get_user_model()로 가져옴)
        # 회원가입에 필요한 필드에 추가로, 선택적으로 성별, 나이, 이미지도 받을 수 있음
        fields = ("email", "password", "nickname", "gender", "age", "image")

    def create(self, validated_data):
        # image 필드가 존재하면 꺼내고, 나머지 데이터는 그대로 사용
        image = validated_data.pop("image", None)
        user = User.objects.create_user(
            email=validated_data["email"],           # 검증된 이메일 값 전달
            password=validated_data["password"],     # 검증된 비밀번호 값 전달
            nickname=validated_data["nickname"],     # 검증된 닉네임 값 전달
            gender=validated_data.get("gender", ""),   # 성별 (기본값은 빈 문자열)
            age=validated_data.get("age")              # 나이 (값이 없으면 None)
        )
        # 이미지가 제공되면, User의 image_url 필드에 할당 후 저장
        if image:
            user.image_url = image
            user.save()
        # 사용자 생성 후 이메일 인증 전송
        send_verification_email(user)
        return user


# 사용자 프로필 Serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # CustomUser 모델 (get_user_model()로 가져옴)
        # 프로필 조회 시, image_url 필드를 포함하여 반환
        fields = ["email", "password", "nickname", "gender", "age", "image_url"]