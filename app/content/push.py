from webpush import send_user_notification


def send_web_push_notification(user, message, head="알림", icon="/static/img/notification-icon.png", url=""):
    payload = {
        "head": head,  # 알림 제목 (기본값: "알림")
        "body": message,  # 알림 본문에 전달된 메시지를 사용
        "icon": icon,  # 알림 아이콘 URL
        "url": url,    # 알림 클릭 시 이동할 URL (필요 시 지정)
    }
    send_user_notification(user=user, payload=payload, ttl=1000)