from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Service)



class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'customer', 'request_date', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100"/>'
        return "No Image"

    display_image.allow_tags = True  # Allows HTML rendering
    display_image.short_description = "Uploaded Image"

admin.site.register(RepairRequest, RepairRequestAdmin)


#admin.site.register(RepairRequest)
