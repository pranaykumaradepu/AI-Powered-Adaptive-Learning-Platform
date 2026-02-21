from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField 
from courses.models import Course, Module

class FocusSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(default=0)
    was_distracted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.duration_minutes} mins"

class SentimentLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Module where the sentiment was detected"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user_message = EncryptedCharField(max_length=5000)
    ai_response_strategy = models.CharField(max_length=100)

    def __str__(self):
        return f"SentimentLog(user={self.user}, module={self.module_id})"
