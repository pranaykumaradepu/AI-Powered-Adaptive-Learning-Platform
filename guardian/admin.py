from django.contrib import admin
from .models import FocusSession,SentimentLog

# Register your models here.
admin.site.register(FocusSession)
admin.site.register(SentimentLog)
