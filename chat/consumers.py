# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser
# from .models import ChatRoom, ChatMessage
# from asgiref.sync import sync_to_async

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_id = self.scope['url_route']['kwargs']['room_id']
#         self.room_group_name = f'chat_{self.room_id}'
#         self.user = self.scope['user']

#         if self.user == AnonymousUser():
#             await self.close()
#             return

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         sender_type = text_data_json.get('sender_type', 'service')  # 'customer' or 'service'

#         # Save message to database
#         room = await sync_to_async(ChatRoom.objects.get)(id=self.room_id)
#         chat_message = await sync_to_async(ChatMessage.objects.create)(
#             room=room,
#             sender=self.user,
#             encrypted_message=b''  # Temporary, will be set in save
#         )
#         await sync_to_async(chat_message.save_encrypted_message)(message)

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message_id': chat_message.id,
#                 'sender_id': self.user.id,
#                 'sender_name': self.user.get_full_name() or self.user.username,
#                 'message': message,
#                 'timestamp': str(chat_message.timestamp),
#                 'is_read': False
#             }
#         )

#     async def chat_message(self, event):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'type': 'chat_message',
#             'message_id': event['message_id'],
#             'sender_id': event['sender_id'],
#             'sender_name': event['sender_name'],
#             'message': event['message'],
#             'timestamp': event['timestamp'],
#             'is_you': event['sender_id'] == self.user.id,
#             'is_read': event['is_read']
#         }))



import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import Message

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        grp_name = 'test'
        self.room_group_name = grp_name
        print("*"*50)
        print(self.room_group_name)
        print("*"*50)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        Message.objects.create(message=message)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))
