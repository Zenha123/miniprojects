from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from users.models import ServiceCenter
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def service_chat(request, customer_id):
    customer = get_object_or_404(User, id=customer_id)
    if not hasattr(request.user, 'servicecenter'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    room, created = ChatRoom.objects.get_or_create(
        customer=customer,
        service_center=request.user
    )
    
    # Mark all messages as read when opening chat
    ChatMessage.objects.filter(room=room, sender=customer).update(is_read=True)
    
    return render(request, 'chat/service_chat.html', {
        'room': room,
        'customer': customer,
    })

@login_required
def get_message_history(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in [room.customer, room.service_center]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
    message_history = []
    for msg in messages:
        message_history.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.get_decrypted_message(),
            'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'is_read': msg.is_read,
            'is_you': msg.sender == request.user,
        })
    
    return JsonResponse({'messages': message_history})

@login_required
def mark_message_read(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    if message.sender == request.user:
        return JsonResponse({'error': 'Cannot mark your own messages as read'}, status=400)
    if request.user not in [message.room.customer, message.room.service_center]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    message.is_read = True
    message.save()
    return JsonResponse({'success': True})