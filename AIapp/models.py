from django.db import models
from django.contrib.auth.models import User

# ===============
# 1つのチャット
# ==============

class Chat(models.Model):

    # このチャットを作ったユーザー
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')

    # サイドバーに表示するチャットのタイトル
    title = models.CharField(max_length=255, blank=True, null=True)

    previous_interaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ===============
# チャット内の1つのメッセージ
# ===============

class Message(models.Model):

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    # どのチャットのメッセージなのか
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')

    # user / assistant
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # メッセージ本文
    content = models.TextField()

    # 送信日時
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat.title} - {self.role}"