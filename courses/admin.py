from django.contrib import admin
from .models import Course, Module, Question

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    inlines = [ModuleInline] 

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_unlocked')
    list_filter = ('course',)
    inlines = [QuestionInline] # This lets you see questions INSIDE the module page

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'module', 'correct_option')
    list_filter = ('module',)