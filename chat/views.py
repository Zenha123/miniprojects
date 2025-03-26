from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import ChatMessage, cipher
from django.db import models

CustomUser = get_user_model()

@login_required
def send_message(request):
    if request.method == "POST":
        sender = request.user
        receiver_id = request.POST.get("receiver_id")
        message = request.POST.get("message")

        if not receiver_id or not message:
            return JsonResponse({"status": "error", "message": "Receiver ID and message are required"})

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            chat_message = ChatMessage(sender=sender, receiver=receiver)
            chat_message.save_encrypted_message(message)
            return JsonResponse({"status": "success"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Receiver not found"})

    # Return a response for GET requests or other unsupported methods
    return HttpResponse("This endpoint only accepts POST requests.", status=405)

@login_required
def get_messages(request, receiver_id):
    try:
        receiver = CustomUser.objects.get(id=receiver_id)
        sender = request.user
        messages = ChatMessage.objects.filter(
            (models.Q(sender=sender, receiver=receiver) | models.Q(sender=receiver, receiver=sender))
        ).order_by('timestamp')

        chat_data = []
        for msg in messages:
            chat_data.append({
                "sender": msg.sender.email,
                "message": msg.get_decrypted_message(),
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })

        return JsonResponse({"messages": chat_data})
    except CustomUser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"})


@login_required
def chat_page(request):
    return render(request, 'chat.html')
