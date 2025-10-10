# api/signals.py

# 【修改】匯入 Django 的 settings，以便讀取寄件人郵件地址
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

# 【修改】移除錯誤的 flask import


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    當密碼重設 token 被建立時，自動發送郵件。
    這個函式會接收到上面提到的「信號」。
    """
    # 建立指向前端重設密碼頁面的 URL，並附上 token
    # 【重要】這是前端頁面的 URL (port 5000)，不是後端 API 的
    reset_password_url = f"http://127.0.0.1:5000/reset-password?token={reset_password_token.key}"

    # 郵件內容
    email_plaintext_message = (
        f"您好 {reset_password_token.user.first_name or reset_password_token.user.username},\n\n"
        "有人請求為您在 MDG Pro 的帳戶重設密碼。\n\n"
        f"請點擊或複製以下連結到瀏覽器中，來設定您的新密碼：\n{reset_password_url}\n\n"
        "如果您沒有請求重設密碼，請直接忽略此郵件。\n\n"
        "謝謝您,\nMDG Pro 團隊"
    )

    # 呼叫 Django 的 send_mail 函式
    # Django 會自動使用我們在 settings.py 中設定的 EMAIL_BACKEND
    # (目前應該是 'console.EmailBackend'，所以會印在終端機上)
    send_mail(
        # 郵件主旨:
        "【MDG Pro】重設您的帳戶密碼",
        # 郵件內容:
        email_plaintext_message,
        # 寄件人: 【修改】從 settings.py 讀取，更具彈性
        settings.DEFAULT_FROM_EMAIL,
        # 收件人:
        [reset_password_token.user.email]
    )