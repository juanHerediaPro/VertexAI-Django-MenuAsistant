# semana/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),        # URL para el front-end
    path('api/chat/', views.chat_api, name='chat_api'), 
    path('api/generate_image/', views.generate_image_api, name='generate_image_api'),# URL para la API
]