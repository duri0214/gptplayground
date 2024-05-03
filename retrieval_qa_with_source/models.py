from django.contrib.auth.models import User
from django.db import models


class ChatLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
