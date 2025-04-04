from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.utils import timezone
import os

class ChatMessage(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.id}"
    
    class Meta:
        ordering = ['timestamp']