from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "topic"],
                name="one_course_per_user_per_topic"
            )
        ]

    def save(self, *args, **kwargs):
        if self.topic:
            self.topic = self.topic.strip().lower()
        super().save(*args, **kwargs)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True) 
    remedial_consumed = models.BooleanField(default=False)

    
    # Content
    resource_url = models.URLField(default='https://google.com')
    warmup_text = models.TextField(default='Legacy content')
    
    # NEW: Assessment Type (Quiz or Code Project?)
    # If True, user must submit code. If False, user takes MCQ quiz.
    is_project_based = models.BooleanField(default=False, help_text="Does this require code submission?")
    
    # NEW: Adaptive Learning Fields (The "Micro-Lesson")
    remedial_text = models.TextField(blank=True, null=True, help_text="Extra lesson if they got a Soft Pass (60-74%)")
    
    # Progression
    is_unlocked = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)


    def __str__(self): return f"{self.order}. {self.title}"

class Question(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.FloatField()
    attempt_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.module} | Attempt {self.attempt_number}"
