import os

import requests

from app.content.email import send_notification_email
from app.content.models import Favorites, Likes
from app.content.push import send_web_push_notification


def kakao_location(location):
    try:
        # 주소 검색 엔드포인트
        url_address = "https://dapi.kakao.com/v2/local/search/address.json"
        # 키워드 검색 엔드포인트
        url_keyword = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {"query": location}  # 검색할 위치 정보
        api_key = os.environ.get("KAKAO_CLIENT_ID")  # 환경 변수에서 API 키 가져오기
        if api_key and not api_key.startswith("KakaoAK"):
            api_key = "KakaoAK " + api_key  # API 키 앞에 접두사 추가  # 없으면 동작안함..
        headers = {"Authorization": api_key, "User-Agent": "bbang-app"}
        # 주소 검색을 시도
        response = requests.get(url_address, params=params, headers=headers)
        data = response.json()
        if data and data.get("documents"):
            document = data["documents"][0]
            if "address" in document:
                lon = document["address"]["x"]
                lat = document["address"]["y"]
                return lat, lon

        # 주소 검색 결과가 없으면 키워드 검색 시도
        response = requests.get(url_keyword, params=params, headers=headers)
        data = response.json()
        if data and data.get("documents"):
            document = data["documents"][0]
            lon = document["x"]
            lat = document["y"]
            return lat, lon

    except Exception as e:
        print("map error:", e)
    return None, None  # 오류나 결과가 없을 경우 None 반환


def Notification_likes_schedule_create_send(schedule):
    # 알림 대상 사용자 리스트 초기화
    if schedule.artist:
        likes = Likes.objects.filter(artist=schedule.artist)
        for like in likes:
            payload = {
                "head": "새 일정 등록 알림",
                "body": f"좋아요하신 아티스트 {schedule.artist.artist_name}의 새 일정 '{schedule.title}'이 등록되었습니다.",
                "icon": "/static/img/notification-icon.png",
                "url": f"https://yourdomain.com/schedules/{schedule.id}/",
            }
            # send_web_push_notification(like.user, payload, 1000)
            send_notification_email(
                subject="새 일정 등록 알림", message=payload["body"], recipient_list=[like.user.email]
            )
    elif schedule.artist_group:
        likes = Likes.objects.filter(artist_group=schedule.artist_group)
        for like in likes:
            payload = {
                "head": "새 일정 등록 알림",
                "body": f"좋아요하신 아티스트 그룹 {schedule.artist_group.artist_group}의 새 일정 '{schedule.title}'이 등록되었습니다.",
                "icon": "/static/img/notification-icon.png",
                "url": f"https://yourdomain.com/schedules/{schedule.id}/",
            }
            # send_web_push_notification(like.user, payload, 1000)
            send_notification_email(
                subject="새 일정 등록 알림", message=payload["body"], recipient_list=[like.user.email]
            )


def Notification_likes_schedule_update_send(schedule):
    favorites = Favorites.objects.filter(schedule=schedule)
    for favorite in favorites:
        payload = {
            "head": "일정 수정 알림",
            "body": f"즐겨찾기하신 일정 '{schedule.title}'이 수정되었습니다.",
            "icon": "/static/img/notification-icon.png",
            "url": f"https://yourdomain.com/schedules/{schedule.id}/",
        }
        # send_web_push_notification(favorite.user, payload, 1000)
        send_notification_email(subject="일정 수정 알림", message=payload["body"], recipient_list=[favorite.user.email])


def Notification_likes_schedule_delete_send(schedule, schedule_title):
    favorites = Favorites.objects.filter(schedule=schedule)
    for favorite in favorites:
        payload = {
            "head": "일정 삭제 알림",
            "body": f"즐겨찾기하신 일정 '{schedule_title}'이 삭제되었습니다.",
            "icon": "/static/img/notification-icon.png",
            "url": "https://yourdomain.com/",  # 삭제 후 이동할 기본 페이지
        }
        # send_web_push_notification(favorite.user, payload, 1000)
        send_notification_email(subject="일정 삭제 알림", message=payload["body"], recipient_list=[favorite.user.email])
