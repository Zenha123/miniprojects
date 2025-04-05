from django.contrib import admin

from .models import *

admin.site.register(CustomUser)
admin.site.register(Customer)
admin.site.register(ServiceCenter)
admin.site.register(Review)

