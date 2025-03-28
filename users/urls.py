from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('signup/',views.signup,name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('sdash/', views.servicedash, name='sdash'),
    path('complete/', views.completed, name='home'),

    path('resend_otp/',views.resend_otp, name='resend_otp'),
    path('cust-dash/', views.cust_dash, name='custdash'),
    path('crepair-status/', views.repair_status, name='custdash'),
]