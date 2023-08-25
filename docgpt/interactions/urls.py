from django.urls import path
from interactions import views


urlpatterns = [
    path('', views.get_answer),
]
