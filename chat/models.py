from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.utils import timezone
import os
from reg.models import *
from users.models import *

class ChatMessage(models.Model):
    request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.id}"
    
    class Meta:
        ordering = ['timestamp']