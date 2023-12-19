import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'

        #joinroom group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        #accept connection
        await self.accept()
    
    async def disconnect(self, close_code):
        #leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    #recieve message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        #send message to WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,{
                'type':'chat_message',
                'message':message,
                'user':self.user.username,
                'datetime': timezone.now.isoformat(),
            }
        )
    
    #receive message from room group
    async def chat_message(self, event):
        #send message to WebSocket
        await self.send(text_data=json.dumps(event))