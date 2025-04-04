from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:request_id>/', views.chat, name='chat'),
]