# Generated by Django 5.1.7 on 2025-03-27 17:40

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("artists", "0001_initial"),
        ("schedule", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Advertisement",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                ("advertisement_type", models.CharField(max_length=50, null=True, verbose_name="광고 타입")),
                ("status", models.BooleanField(default=False, null=True, verbose_name="광고 상태")),
                ("sent_at", models.DateTimeField(null=True, verbose_name="광고 전송시간")),
                (
                    "image_url",
                    models.ImageField(
                        blank=True, null=True, upload_to="Advertisement_images/", verbose_name="광고 이미지"
                    ),
                ),
                ("link_url", models.CharField(max_length=255, null=True, verbose_name="링크 URL")),
                ("start_date", models.DateTimeField(null=True, verbose_name="시작일")),
                ("end_date", models.DateTimeField(null=True, verbose_name="종료일")),
            ],
            options={
                "verbose_name": "광고",
                "verbose_name_plural": "광고 목록",
                "db_table": "advertisement",
            },
        ),
        migrations.CreateModel(
            name="authority",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                ("artistName", models.CharField(max_length=20, verbose_name="아티스트(개인, 그룹) 이름")),
                ("artist_agency", models.CharField(max_length=20, verbose_name="소속사")),
                ("phone_number", models.CharField(max_length=15, verbose_name="전화번호")),
                (
                    "image_url",
                    models.ImageField(blank=True, null=True, upload_to="authority/", verbose_name="첨부파일"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="신청 유저",
                    ),
                ),
            ],
            options={
                "verbose_name": "권한 신청",
                "verbose_name_plural": "권한 신청 목록",
            },
        ),
        migrations.CreateModel(
            name="Favorites",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                (
                    "schedule",
                    models.ForeignKey(
                        db_column="schedule_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule.schedule",
                        verbose_name="일정",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "즐겨찾기",
                "verbose_name_plural": "즐겨찾기 목록",
                "db_table": "favorites",
            },
        ),
        migrations.CreateModel(
            name="Likes",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                (
                    "artist",
                    models.ForeignKey(
                        blank=True,
                        db_column="artist_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="artists.artist",
                        verbose_name="아티스트",
                    ),
                ),
                (
                    "artist_group",
                    models.ForeignKey(
                        blank=True,
                        db_column="artist_group_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="artists.artistgroup",
                        verbose_name="아티스트 그룹",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "좋아요",
                "verbose_name_plural": "좋아요 목록",
                "db_table": "likes",
            },
        ),
        migrations.CreateModel(
            name="Notifications",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                ("is_active", models.BooleanField(default=False, null=True, verbose_name="알림 활성 여부")),
                (
                    "favorites",
                    models.ForeignKey(
                        blank=True,
                        db_column="favorites_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="content.favorites",
                        verbose_name="즐겨찾기",
                    ),
                ),
                (
                    "likes",
                    models.ForeignKey(
                        blank=True,
                        db_column="likes_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="content.likes",
                        verbose_name="좋아요",
                    ),
                ),
            ],
            options={
                "verbose_name": "알림",
                "verbose_name_plural": "알림 목록",
                "db_table": "notifications",
            },
        ),
    ]
