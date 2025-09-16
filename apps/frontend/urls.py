from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evaluate/', views.evaluate_report, name='evaluate_report'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]


