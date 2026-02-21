from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Intake Information
    goal_purpose = models.TextField(help_text="Why are you learning this?")
    current_knowledge_level = models.IntegerField(default=1, help_text="Scale 1-10")
    preferred_topics = models.CharField(max_length=255, help_text="e.g., Python, React")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"