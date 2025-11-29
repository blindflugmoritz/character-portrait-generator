"""
URL routing for API endpoints
"""
from django.urls import path
from . import views

urlpatterns = [
    path('generate-crew', views.generate_crew, name='generate_crew'),
    path('analyze-photo', views.analyze_photo, name='analyze_photo'),
]
