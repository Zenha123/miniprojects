
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,Group,Permission
import re
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
         if not email:
              raise ValueError("Email is required")
         email = self.normalize_email(email)
         user = self.model(email=email,**extra_fields)
         user.set_password(password)
         user.save(using=self._db)
         return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(max_length=50, choices=[('Customer', 'Customer'), ('Agent', 'Agent')])
    groups = None
    user_permissions = None
     
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phoneno = models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return self.name + str(self.id)
    
class ServiceCenter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    address = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name

