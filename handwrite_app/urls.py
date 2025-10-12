from django.urls import path
from . import views

app_name = 'handwrite'

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze_prescription, name='analyze_prescription'),
    path('extract-text/', views.extract_text, name='extract_text'),
    path('health/', views.health_check, name='health_check'),
]
