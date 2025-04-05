from django.db import models
from users.models import *
#from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class Product(models.Model):
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    model_number = models.CharField(max_length=100)
    purchase_date = models.DateField()
    warranty_status = models.IntegerField(help_text="Warranty period in months")
    def __str__(self):
        return self.product_name
        


class Service(models.Model):

        service = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
        service_name = models.CharField(max_length=1000,blank=True)
        
        
        def __str__(self):
            return f"{self.service_name} ({self.service.name})"

class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('waiting_for_parts', 'Waiting for Parts'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)  # Link request to customer
    product_name = models.CharField(max_length=255)
    issue_description = models.TextField()
    address = models.CharField(max_length=255)
    preferred_location = models.CharField(max_length=255, blank=True, null=True)
    service_center = models.ForeignKey('users.ServiceCenter', on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="repair_images/", blank=True, null=True)
    contact_no = models.CharField(max_length=10,blank=True,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
    completed_date = models.DateTimeField(null=True, blank=True)




    ###3#
    @property
    def has_review(self):
        return hasattr(self, 'review')

    def __str__(self):
        return f"Repair Request for {self.product_name} at {self.service_center.name}"







