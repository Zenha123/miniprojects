
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import CustomUser, Customer, ServiceCenter, OTP
from .forms import CustomUserCreationForm, CustomerForm, ServiceCenterForm, OTPForm
from django.core.mail import send_mail
import pyotp
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render,redirect
from reg.models import RepairRequest

User= get_user_model()
@csrf_exempt


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('repairreq')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

def forgot_password(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'No user found with this email.'})
        
        # Generate a password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"{settings.BASE_URL}/reset-password/{uid}/{token}/"

        subject = 'Password Reset Request'
        message = f'''
        Hello{user.email},

        you requested a password reset.please click on the link below to reset your password:
        {reset_link}

        If you did not request this,please ignore this mail.

        Thank You,
        ReparoHub
        '''

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        return render(request, 'users/forgot_password.html', {'message': 'A password reset link has been sent to your email.'})
    
    return render(request, 'users/forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverFlowError, User.DoesNotExist):
        user=None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return render(request, 'users/reset_password.html', {'error': 'Passwords do not match.'})

            # Update the user's password
            user.password = make_password(password)
            user.save()

            return render(request, 'users/login.html', {'message': 'Your password has been reset successfully.'})

        return render(request, 'users/reset_password.html')
    else:
        return render(request, 'users/reset_password.html', {'error': 'Invalid or expired reset link.'})



def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        name = request.POST.get('name')
        location = request.POST.get('location', None)

        if password1 != password2:
            return render(request, 'users/signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            return render(request, 'users/signup.html', {'error': 'Email already exists. Do you want to <a href="/login/">log in</a>? Or please use a different email.'})

        # Store user data in session
        request.session['signup_data'] = {
            'email': email,
            'password': password1,
            'user_type': user_type,
            'name': name,
            'location': location,
        }

        # Generate OTP
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
        expires_at = timezone.now() + timedelta(minutes=5)
        request.session['otp'] = otp
        request.session['otp_expires_at'] = expires_at.isoformat()


        # Send OTP via email
        send_otp_email(email, otp, name)

        # Redirect to verify_otp with a placeholder user_id (e.g., 0)
        return redirect('verify_otp')  # Pass a placeholder user_id

    return render(request, 'users/signup.html')

def verify_otp(request):
    message = request.session.pop('message',None)

    if request.method == 'POST':
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1,7)])
        otp = request.session.get('otp')
        expires_at = request.session.get('otp_expires_at')


        if not otp or not expires_at:
            return render(request, 'users/verify_otp.html', {'error': 'OTP expired or invalid', 'message':message})

        if timezone.now() > timezone.datetime.fromisoformat(expires_at):
            return render(request, 'verify_otp.html', {'error': 'OTP expired'})

        if otp_entered == otp:
            # Create user
            signup_data = request.session.get('signup_data')
            if not signup_data:
                return render(request, 'users/verify_otp.html', {'error': 'Invalid session data','message':message})

            user = User.objects.create_user(
                email=signup_data['email'],
                password=signup_data['password'],
                user_type=signup_data['user_type'],
            )
            user.is_active = True
            user.save()

            # Create Customer or Service Center profile
            if signup_data['user_type'] == 'Customer':
                Customer.objects.create(user=user, name=signup_data['name'])
            elif signup_data['user_type'] == 'Service Center':
                ServiceCenter.objects.create(user=user, name=signup_data['name'], location=signup_data['location'])

            # Clear session data
            request.session.pop('signup_data')
            request.session.pop('otp')
            request.session.pop('otp_expires_at')

            # Log the user in
            login(request, user)
            return redirect('product_reg')

        else:
            return render(request, 'users/verify_otp.html', {'error': 'Invalid OTP', 'message':message})

    return render(request, 'users/verify_otp.html',{'message': message})

def send_otp_email(email, otp, username):
    print(f"Sending OTP {otp} to {email}")  # Debugging
    subject = "your OTP for signup"
    message = message = f'''
    Hey {username},

    Welcome to our platform! We're excited to have you on board.

    Your signup OTP is: {otp}

    Please use this OTP to complete your registration. This OTP is valid for 5 minutes.

    Thank you for choosing us!

    Best regards,
    ReparoHub
    '''
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)


def home(request):
    return render(request, 'users/home.html')


def servicedash(request):
    
    if not hasattr(request.user, 'servicecenter'):
        return HttpResponseForbidden("Access denied")
    
    service_center = request.user.servicecenter
    repair_requests = RepairRequest.objects.filter(service_center=service_center)
    pending_requests = repair_requests.filter(status__in=['pending', 'in_progress'])
    
    return render(request, 'service/dashboard.html', {
        'repair_requests': repair_requests,
        'pending_requests': pending_requests,
    })



    return render(request, 'users/service-dash.html')

def completed(request):
    return render(request, 'users/complete.html')


def resend_otp(request):
    if 'signup_data' in request.session:
        #generating new otp
        totp = pyotp.TOTP(pyotp.random_base32())
        otp=totp.now()
        expires_at = timezone.now()+ timedelta(minutes=5)

        request.session['otp'] = otp
        request.session['otp_expires_at'] = expires_at.isoformat()

        email = request.session['signup_data']['email']
        name = request.session['signup_data']['name']
        send_otp_email(email, otp, name)

        request.session['message'] = 'A new OTP has been sent to your email.'

    return redirect('verify_otp')

def cust_dash(request):
    return render(request, 'users/cust_dash.html')


def repair_status(request):
    return render(request, 'users/repairstatus.html')

