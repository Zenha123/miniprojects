
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
from django.contrib import messages
from reg.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect,get_object_or_404
from reg.models import RepairRequest

######
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
#from .models import RepairRequest, Review
from .forms import ReviewForm
from django.db.models import Q 




User= get_user_model()
@csrf_exempt


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'Customer':
                return redirect('custdash')
            elif user.user_type == 'Service Center':
                return redirect('sdash')
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
            return redirect('home')

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



@login_required
def cust_dash(request):
    if request.user.user_type != 'Customer':
        return redirect('login')
    

    try:
        customer_profile = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        customer_profile = None

    active_repairs = RepairRequest.objects.filter(
        customer=request.user
    ).exclude(
        status__in=['completed', 'cancelled']
    ).count()

    completed_repairs = RepairRequest.objects.filter(
        customer=request.user,
        status='completed'
    ).count()

    customer_products = Product.objects.filter(customer__user=request.user)


    context = {
        'customer': request.user,
        'customer_profile': customer_profile,
        'active_repairs': active_repairs,
        'completed_repairs': completed_repairs,
        'customer_products': customer_products,
    }
    return render(request, 'users/cust_dash.html', context)
    

def show_service_centers(request):
    service_centers = ServiceCenter.objects.all().order_by('name')

    context = {
        'service_centers': service_centers
    }
    return render(request, 'users/showing.html', context)
    

def service_center_detail(request, center_id):
    service_center = get_object_or_404(ServiceCenter, user_id=center_id)
    
    # Get services provided by this center
    services = Service.objects.filter(service=service_center)
    
    # Get reviews for this center
    #reviews = Review.objects.filter(service_center=service_center)
    
    # Get service history for the current user (if logged in)
    service_history = []
    if request.user.is_authenticated:
        service_history = RepairRequest.objects.filter(
            customer=request.user,
            service_center=service_center
        ).order_by('-request_date')
    
    context = {
        'service_center': service_center,
        'services': services,
        #'reviews': reviews,
        'service_history': service_history
    }
    return render(request,'users/service-detail.html',context)


# @login_required
# def repair_status(request):
#     if request.user.user_type != 'Customer':
#         return redirect('login')
    
#     try:
#         customer_profile = Customer.objects.get(user=request.user)
#     except Customer.DoesNotExist:
#         customer_profile = None

#     active_repairs = RepairRequest.objects.filter(
#         customer=request.user
#     ).exclude(
#         status__in=['completed', 'cancelled']
#     )

#     completed_repairs = RepairRequest.objects.filter(
#         customer=request.user,
#         status='completed'
#     )
#     context = {
#         'active_repairs': active_repairs,
#         'completed_repairs': completed_repairs,
#     }
#     return render(request, 'users/repairstatus.html', context)

######
def repair_status(request):
    # Redirect non-customers
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'Customer':
        return redirect('login')
    
    # Get active repairs (excluding completed/cancelled)
    active_repairs = RepairRequest.objects.filter(
        customer=request.user
    ).exclude(
        status__in=['Completed', 'Cancelled', 'completed', 'cancelled']  # Handle both cases
    )

    # Get completed repairs (case-insensitive)
    completed_repairs = RepairRequest.objects.filter(
        customer=request.user
    ).filter(
        Q(status='Completed') | Q(status='completed')
    )

    context = {
        'active_repairs': active_repairs,
        'completed_repairs': completed_repairs,
    }
    return render(request, 'users/repairstatus.html', context)

@login_required
def servicedash(request):
    try:
        service_center = request.user.servicecenter
    except:
        messages.error(request, 'you are not associated with any service center')
        return redirect('login')
    pending_requests = RepairRequest.objects.filter(service_center=service_center,status='pending')
    
    in_progress_requests = RepairRequest.objects.filter(
        service_center=service_center,
        status='in_progress'
    )

    context = {'pending_requests':pending_requests,
            'in_progress_requests': in_progress_requests}
    
    return render(request, 'users/service-dash.html',context)

@login_required
def update_request_status(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    if repair_request.service_center != request.user.servicecenter:
        messages.error(request,"you are not authorized to update this request.")
        return redirect('sdash')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(RepairRequest.STATUS_CHOICES).keys():
            repair_request.status = new_status
            repair_request.save()
            messages.success(request,f"Request status updated to {new_status}.")

        else:
            messages.error(request,"Invalid status.")

    return redirect('sdash')


def active_repairs_view(request):
    if not hasattr(request.user, 'servicecenter'):
        raise PermissionDenied("Service center profile required")
    # Get requests that are accepted but not completed
    active_requests = RepairRequest.objects.filter(
        service_center=request.user.servicecenter,
        status__in=['accepted', 'in_progress', 'waiting_for_parts', 'ready_for_pickup']
    ).order_by('-request_date')
    
    context = {
        'active_requests': active_requests
    }

    return render(request, 'users/active_repairs.html', context)


@login_required
def request_detail(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id, service_center=request.user.servicecenter)
    # Check if user has permission to view this request
    if not (request.user == repair_request.customer or (hasattr(request.user, 'servicecenter') and request.user.servicecenter == repair_request.service_center)):
        raise PermissionDenied
    
    context = {
        'repair_request': repair_request,
        'user_is_service_center': hasattr(request.user, 'servicecenter')
    }
    return render(request, 'users/request_detail.html', context)
    

class RepairStatusLog(models.Model):
    repair = models.ForeignKey(RepairRequest, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=RepairRequest.STATUS_CHOICES)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.repair} → {self.status} at {self.changed_at}"

def completed(request):
    service_center = get_object_or_404(ServiceCenter, user=request.user)
    
    # Filter completed requests for this service center
    completed_requests = RepairRequest.objects.filter(
        service_center=service_center,
        status='completed'
    ).order_by('-completed_date')  # Newest first
    
    context = {
        'completed_requests': completed_requests,
        'service_center': service_center
    }
    return render(request, 'users/complete.html', context)
   

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


############

@login_required
def submit_review(request, repair_id):
    repair = get_object_or_404(RepairRequest, id=repair_id, customer=request.user)
    
    # Check if review already exists
    if hasattr(repair, 'review'):
        return redirect('view_review', repair_id=repair.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.repair_request = repair
            review.service_center = repair.service_center
            review.customer = request.user
            review.save()
            return redirect('repairstatus')
    else:
        form = ReviewForm()
    
    return render(request, 'users/feedback.html', {
        'form': form,
        'repair': repair,
        'service_center': repair.service_center,
    })

@login_required
def view_review(request, repair_id):
    repair = get_object_or_404(RepairRequest, id=repair_id, customer=request.user)
    review = get_object_or_404(Review, repair_request=repair)
    return render(request, 'users/review.html', {
        'review': review,
        'repair': repair,
    })





