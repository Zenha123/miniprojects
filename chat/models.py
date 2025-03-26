
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.utils import timezone
from users.models import *

# Ensure the encryption key is securely managed
key = Fernet.generate_key()
cipher = Fernet(key)

class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    encrypted_message = models.BinaryField()  # Storing encrypted message as binary
    timestamp = models.DateTimeField(auto_now_add=True)
    


    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email}"

    def save_encrypted_message(self, message):
        """Encrypts and saves the message."""
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        self.encrypted_message = encrypted_message
        self.save()

    def get_decrypted_message(self):
        """Decrypts and returns the message."""
        decrypted_message = cipher.decrypt(self.encrypted_message).decode('utf-8')
        return decrypted_message