from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import *
from users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import*

"""def product_reg(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        model_number = request.POST.get("model_number")
        purchase_date = request.POST.get("purchase_date")
        warranty_status = request.POST.get("warranty_period")

        if not (product_name and model_number and purchase_date and warranty_status):
            messages.error(request, "All fields are required.")
            return redirect("product_reg")

        product = Product.objects.create(
            user=request.user,
            customer=customer,  
            product_name=product_name,
            model_number=model_number,
            purchase_date=purchase_date,
            warranty_status=warranty_status
        )
       
        messages.success(request, "Product registered successfully!")
        return redirect("dashboard")
    return render(request, 'productreg.html')"""



def product_reg(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        model_number = request.POST.get("model_number")
        purchase_date = request.POST.get("purchase_date")
        warranty_status = request.POST.get("warranty_period")

        if not (product_name and model_number and purchase_date and warranty_status):
            messages.error(request, "All fields are required.")
            return redirect("product_reg")

        # ✅ Get the customer instance
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "Customer profile not found.")
            return redirect("product_reg")

        # ✅ Create the product
        Product.objects.create(
            customer=customer,  # Correctly pass Customer instance
            product_name=product_name,
            model_number=model_number,
            purchase_date=purchase_date,
            warranty_status=warranty_status
        )

        messages.success(request, "Product registered successfully!")
        return redirect("")

    return render(request, "productreg.html")


 

"""def user_dashboard(request):
    products = Product.objects.filter(user=request.user)  # Get products of logged-in user
    return render(request, "product/user-dashboard.html", {"products": products})"""

@login_required
def user_dashboard(request):
    try:
        customer = Customer.objects.get(user=request.user)
        products = Product.objects.filter(customer=customer)  # ✅ Filter by `customer`
    except Customer.DoesNotExist:
        products = []

    return render(request, "product/user-dashboard.html", {"products": products})




def service_reg(request):
    return render(request, 'servicereg.html')


"""@login_required(login_url="/admin/") 
def repair_req(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        issue_description = request.POST.get("issue_description")
        address = request.POST.get("address")
        preferred_location = request.POST.get("preferred_location")
        service_center = request.POST.get("service_center")
        image = request.FILES.get("image")

        if not (product_name and issue_description and address):
            messages.error(request, "All fields are required.")
            return redirect("repair_request")

       
        RepairRequest.objects.create(
            customer=request.user,  
            product_name=product_name,
            issue_description=issue_description,
            address=address,
            preferred_location=preferred_location,
            service_center=service_center,
            image=image
        )

        messages.success(request, "Repair request submitted successfully!")
        return redirect("dashboard")

    return render(request, "repair.html")"""






@login_required(login_url="/admin/") 
def repair_req(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        issue_description = request.POST.get("issue_description")
        address = request.POST.get("address")
        preferred_location = request.POST.get("preferred_location")
        service_center = request.POST.get("service_center")
        image = request.FILES.get("image")

        if not (product_name and issue_description and address):
            messages.error(request, "All fields are required.")
            return redirect("repair")

        # ✅ Get the customer instance
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "Customer profile not found.")
            return redirect("repair_request")
        
        service_center_name = request.POST.get("service_center")  # Get service center name as string
        try:
            service_center = ServiceCenter.objects.get(name=service_center_name)
        except ServiceCenter.DoesNotExist:
             messages.error(request, "Service center not found!")
             return redirect("repair_request")  # Redirect to the form page

        # ✅ Create repair request
        RepairRequest.objects.create(
            #customer=customer,
            customer=request.user,   
            product_name=product_name,
            issue_description=issue_description,
            address=address,
            preferred_location=preferred_location,
            service_center=service_center,
            image=image
        )

        messages.success(request, "Repair request submitted successfully!")
        return redirect("dashboard")

    return render(request, "repair.html")


"""def fetch_service_centers(request):
    location = request.GET.get('location')
    centers = ServiceCenter.objects.filter(location__icontains=location).values('name', 'address')
    return JsonResponse({"centers": list(centers)})"""



def fetch_service_centers(request):
    location = request.GET.get('location', '')
    centers = ServiceCenter.objects.filter(location__icontains=location).values('name', 'location')  # ✅ Use `location`

    return JsonResponse({"centers": list(centers)})

