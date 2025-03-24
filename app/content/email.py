from django.conf import settings
from django.core.mail import send_mail


# 생성, 수정, 삭제 필드
def send_notification_email(subject, message, recipient_list):
    main_page_link = settings.SITE_URL  # 필요에 따라 별도의 MAIN_PAGE_URL 설정 가능

    # HTML 메시지 구성: 본문 내용과 메인 페이지로 이동할 수 있는 링크 포함
    html_message = f"""
    <html>
      <body style="font-family: 'Arial', sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2>{subject}</h2>
          <p>{message}</p>
          <p>더 자세한 내용은 아래 링크를 클릭해주세요.</p>
          <p>
          <br>
            <a href="{main_page_link}" style="background-color: #02b875; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 3px;">
              메인 페이지로 이동
            </a>
          </p>
        </div>
      </body>
    </html>
    """

    # send_mail 함수를 사용하여 이메일 전송
    send_mail(
        subject,  # 이메일 제목
        message,  # 기본 텍스트 메시지 (대체 텍스트)
        settings.DEFAULT_FROM_EMAIL,  # 발신자 이메일 주소
        recipient_list,  # 수신자 리스트
        html_message=html_message,  # HTML 형식 메시지
        fail_silently=False,  # 오류 발생 시 예외 발생 (개발 단계에서 False 설정)
    )
