from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.accounts.email import send_verification_email

User = get_user_model()


# 회원가입 Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # write_only => 입력 시에만 사용되고 응답 시에는 노출되지 않음

    class Meta:
        model = User  # 모델 설정 <=> CustomUser 모델 <=> User = get_user_model
        fields = ("email", "password", "nickname")  # 수정 목록 정하는 필드

    def create(self, validated_data):
        user = User.objects.create_user(  # 사용자 생성
            email=validated_data["email"],  # 검증된 이메일 값 전달
            password=validated_data["password"],  # 검증된 비밀번호 값 전달
            nickname=validated_data["nickname"],  # 검증된 닉네임 값 전달
        )
        send_verification_email(user)  # 사용자 생성 후 이메일 전송 함수로 넘어가서 이메일 전송
        return user  # 생성된 사용자 반환


# 사용자 직렬화 Serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # 모델 설정 <=> CustomUser 모델 <=> User = get_user_model
        fields = ["email", "password", "nickname", "gender", "age"]  # 수정 목록 + 보여줌
