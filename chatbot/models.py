# Create your models here.
from django.db import models
from django.utils import timezone

class ChatSession(models.Model):
    created_at = models.DateTimeField(default=timezone.now)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'user' or 'bot'
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
