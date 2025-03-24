import datetime

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from app.accounts.email import send_verification_email

User = get_user_model()


# 회원가입 Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 비밀번호는 쓰기 전용으로 설정
    # 프론트엔드에서 base64 인코딩된 이미지를 "image" 키로 전달하면 처리함
    image_url = Base64ImageField(required=False, allow_null=True)
    # 나이와 성별은 선택적으로 전달 있으면 나이 없으면 null값
    gender = serializers.CharField(required=False, allow_blank=True)
    age = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User  # User 모델
        fields = ("email", "password", "nickname", "gender", "age", "image_url")

    def create(self, validated_data):
        # image 필드가 존재하면 꺼내고, 나머지 데이터는 그대로 사용
        image_url = validated_data.pop("image_url", None)
        # 성별은 없으면 빈 문자열로 처리
        gender = validated_data.get("gender", "")
        # 나이 필드 처리: 프론트에서 출생년도를 전달하는 경우 (예: "2000")
        birth_year = validated_data.get("age")
        if birth_year:
            try:
                # 출생년도를 정수로 변환 후, 한국식 나이 계산: (현재 연도 - 출생년도 + 1)
                birth_year_int = int(birth_year)
                current_year = datetime.date.today().year
                computed_age = current_year - birth_year_int + 1
            except ValueError:
                # 변환 실패 시 None으로 처리
                computed_age = None
        else:
            computed_age = None

        # validated_data에 계산된 나이 저장 (정수 값 또는 None)
        validated_data["age"] = computed_age
        validated_data["gender"] = gender

        user = User.objects.create_user(
            email=validated_data["email"],  # 검증된 이메일 값 전달
            password=validated_data["password"],  # 검증된 비밀번호 값 전달
            nickname=validated_data["nickname"],  # 검증된 닉네임 값 전달
            gender=validated_data.get("gender", ""),  # 성별 (기본값은 빈 문자열)
            age=validated_data.get("age"),  # 계산된 나이 (정수 또는 None)
        )
        # 이미지가 제공되면, User의 image_url 필드에 할당 후 저장
        if image_url:
            user.image_url = image_url
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
