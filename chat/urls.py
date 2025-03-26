from django.urls import path
from . import views

urlpatterns = [
    # Render the chat page
    path('chat/', views.chat_page, name='chat'),

    # Handle chat messages
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/<int:receiver_id>/', views.get_messages, name='get_messages'),
]
