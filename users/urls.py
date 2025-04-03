from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('signup/',views.signup,name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('sdash/', views.servicedash, name='sdash'),
    path('complete/', views.completed, name='complete'),

    path('resend_otp/',views.resend_otp, name='resend_otp'),
    path('cust-dash/', views.cust_dash, name='custdash'),
    path('crepair-status/', views.repair_status, name='repairstatus'),

    path('active-repairs/', views.active_repairs_view, name='active_repairs'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('update-status/<int:request_id>/', views.update_request_status, name='update_request_status'),
]