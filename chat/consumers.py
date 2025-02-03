import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

from .models import Message, ChatRoom
from django.core.files.base import ContentFile
import base64

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        image_data = data.get('image', None)  # Receive image in Base64

        sender = self.scope['user']
        chatroom = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)

        image_url = None
        timestamp = timezone.now()
        if image_data:
            

            # Decode Base64 image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"{sender.username}_image.{ext}")

            # Save the message with the image
            message_obj = await sync_to_async(Message.objects.create)(
                chatroom=chatroom,
                sender=sender,
                image=image_file,
                timestamp=timestamp
            )
            image_url = message_obj.image.url
        elif message:
            # Save the message without an image
            await sync_to_async(Message.objects.create)(
                chatroom=chatroom,
                sender=sender,
                message=message,
                timestamp=timestamp
            )

        # Send message and image URL to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': sender.username,
                'image_url': image_url,
                'timestamp': timestamp.isoformat(),
            }
        )

    async def chatroom_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'image_url': event['image_url'],
            'timestamp': event['timestamp']
        }))