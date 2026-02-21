from django.urls import path
from .views import create_course_view, dashboard_view, course_detail_view, take_quiz_view

urlpatterns = [
    path('create/', create_course_view, name='create_course'),
    path('dashboard/', dashboard_view, name='dashboard'),

    path('<int:course_id>/', course_detail_view, name='course_detail'),
    path('<int:course_id>/module/<int:module_id>/', course_detail_view, name='course_module'),
    path('<int:course_id>/module/<int:module_id>/quiz/', take_quiz_view, name='take_quiz'),


]
