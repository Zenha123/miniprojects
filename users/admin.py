from django.contrib import admin

from .models import *


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
    )
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Customer)
admin.site.register(ServiceCenter)
admin.site.register(Review)