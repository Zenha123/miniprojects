from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatMessage
import json
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'
        self.user = self.scope["user"]

        # First accept the connection to allow sending error messages
        await self.accept()

        # Verify user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.send(json.dumps({
                'error': 'Authentication required',
                'type': 'error'
            }))
            await self.close(code=4001)
            return

        try:
            # Verify request exists and user has permission
            self.service_request = await self.get_service_request()
            if not await self.user_has_permission():
                await self.send(json.dumps({
                    'error': 'Permission denied',
                    'type': 'error'
                }))
                await self.close(code=4003)
                return
        except ObjectDoesNotExist:
            await self.send(json.dumps({
                'error': 'Chat room not found',
                'type': 'error'
            }))
            await self.close(code=4004)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.send_existing_messages()

    @sync_to_async
    def get_service_request(self):
        return RepairRequest.objects.select_related('customer', 'agent').get(
            id=self.request_id,
            status='accepted'
        )

    @sync_to_async
    def user_has_permission(self):
        return self.user.id in [self.service_request.customer.id, self.service_request.agent.id]

    async def send_existing_messages(self):
        messages = await self.get_messages()
        for message in messages:
            await self.send_message_to_client({
                'type': 'chat_message',
                'message': message.message,
                'sender': message.sender.username,
                'sender_id': message.sender.id,
                'timestamp': message.timestamp.isoformat(),
                'db_id': str(message.id)
            })

    @sync_to_async
    def get_messages(self):
        return list(ChatMessage.objects.filter(
            request_id=self.request_id
        ).select_related('sender').order_by('timestamp'))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if 'message' not in data:
                raise ValueError("Missing message field")
                
            message = await self.save_message(data['message'])
            await self.broadcast_message({
                'type': 'chat_message',
                'message': message.message,
                'sender': message.sender.username,
                'sender_id': message.sender.id,
                'timestamp': message.timestamp.isoformat(),
                'db_id': str(message.id)
            })
        except Exception as e:
            print(f"Error processing message: {e}")
            await self.send_error("Failed to process message")

    @sync_to_async
    def save_message(self, message_content):
        return ChatMessage.objects.create(
            request_id=self.request_id,
            sender=self.user,
            message=message_content
        )

    async def broadcast_message(self, message_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    async def send_message_to_client(self, message_data):
        await self.send(text_data=json.dumps(message_data))

    async def send_error(self, error_message):
        await self.send_message_to_client({
            'type': 'error',
            'error': error_message
        })

    async def chat_message(self, event):
        await self.send_message_to_client(event)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )