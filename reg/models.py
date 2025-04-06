from django.db import models
from users.models import *
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
###
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

# class Product(models.Model):
#     customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
#     product_name = models.CharField(max_length=255)
#     model_number = models.CharField(max_length=100)
#     purchase_date = models.DateField()
#     #warranty_status = models.IntegerField(help_text="Warranty period in months")
#     warranty_status = models.IntegerField(
#         null=True,  # Make it nullable
#         blank=True,  # Allow blank in forms
#         help_text="Warranty period in months"
#     )
#     def __str__(self):
#         return self.product_name
        

#warrenty###3
class Product(models.Model):
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    model_number = models.CharField(max_length=100)
    purchase_date = models.DateField()
    warranty_end_date = models.DateField(null=True, blank=True)  # Optional warranty
    notified = models.BooleanField(default=False)  # Track if notified
    
    def __str__(self):
        return self.product_name
    
    def check_warranty(self):
        """Check if warranty is about to expire"""
        if self.warranty_end_date and not self.notified:
            one_day_before = self.warranty_end_date - timedelta(days=1)
            if timezone.now().date() >= one_day_before:
                self.send_notification()
                self.notified = True
                self.save()
    
    def send_notification(self):
        """Send warranty expiration email"""
        send_mail(
            subject=f"⚠️ Warranty Expiring: {self.product_name}",
            message=f"""Dear Customer,

Your {self.product_name} (Model: {self.model_number}) 
warranty expires on {self.warranty_end_date}.

Please consider any final repairs.

Thank you,
ReparoHub Team""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.customer.user.email],
        )



        

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







