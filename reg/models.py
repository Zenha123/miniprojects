from django.db import models
from users.models import *



class Product(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
        product_name = models.CharField(max_length=255)
        model_number = models.CharField(max_length=100)
        purchase_date = models.DateField()
        warranty_status = models.IntegerField(help_text="Warranty period in months")
        def __str__(self):
            return self.product_name
        


class Service(models.Model):
        service = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
        service_catalog = models.CharField(max_length=1000,blank=True)
        contact_no = models.CharField(max_length=10,blank=True,null=True)
        def __str__(self):
            return self.service
