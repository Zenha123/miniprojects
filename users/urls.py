from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('cust-dash/', views.cust_dash, name='custdash'),
    path('crepair-status/', views.repair_status, name='custdash'),
]