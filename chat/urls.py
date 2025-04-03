from django.urls import path
from . import views

urlpatterns = [
    path('service/<int:customer_id>/', views.service_chat, name='service_chat'),
    path('api/messages/<int:room_id>/', views.get_message_history, name='message_history'),
    path('api/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
]