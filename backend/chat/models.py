from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]

    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    message  = models.TextField()
    time = models.DateTimeField(default=timezone.now)

