from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from users.models import ServiceCenter
from reg.models import RepairRequest
from django.contrib.auth import get_user_model
from .forms import *

User = get_user_model()

@login_required
def chat(request, request_id):
    service_request = get_object_or_404(RepairRequest, id=request_id)
    
    # Check if user is part of this request
    if request.user not in [service_request.customer, service_request.service_center]:
        return redirect('custdash')
    
    # Only allow chat if request is accepted
    if service_request.status != 'accepted':
        return redirect('custdash')
    
    messages = ChatMessage.objects.filter(request=service_request).order_by('timestamp')
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.request = service_request
            chat_message.sender = request.user
            chat_message.save()
            return redirect('chat', request_id=request_id)
    else:
        form = ChatMessageForm()
    
    return render(request, 'chat.html', {
        'service_request': service_request,
        'messages': messages,
        'form': form,
        'other_user': service_request.service_center if request.user == service_request.customer else service_request.customer
    })