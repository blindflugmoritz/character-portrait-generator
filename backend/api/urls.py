"""
URL routing for API endpoints
"""
from django.urls import path
from . import views
from .views_postcard import generate_postcard_api

urlpatterns = [
    path('generate-crew', views.generate_crew, name='generate_crew'),
    path('analyze-photo', views.analyze_photo, name='analyze_photo'),
    path('generate-postcard', generate_postcard_api, name='generate_postcard'),
    path('version-check', views.version_check, name='version_check'),
    path('health', views.health_check, name='health_check'),
]
