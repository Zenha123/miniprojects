from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('productreg/', product_reg, name='product_register'),
    path('dashboard/', user_dashboard, name="dashboard"),
    path('servicereg/', service_reg, name='service_register'),
    path('repairreq/', repair_req, name='repairreq'),
    path('fetch_service_centers/', fetch_service_centers, name='fetch_service_centers'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)