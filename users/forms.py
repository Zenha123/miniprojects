from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Customer, ServiceCenter, OTP

from django import forms

# from reg.models import Review 


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model=CustomUser
        fields = ['email', 'password1', 'password2', 'user_type']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']

class ServiceCenterForm(forms.ModelForm):
    class Meta:
        model=ServiceCenter
        fields = ['name', 'location']

class OTPForm(forms.Form):
    otp=forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'otp-box'}))





