
import json
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_box_name = self.scope["url_route"]["kwargs"]["chat_box_name"]
        self.group_name = "chat_%s" % self.chat_box_name

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
    

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "username": username,
            },
        )
    # Receive message from room group.
    async def chatbox_message(self, event):
        message = event["message"]
        username = event["username"]
        #send message and username of sender to websocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                }
            )
        )
    pass
class NoftificationConsumer(AsyncWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi lại thông báo cho client
        self.send(text_data=json.dumps({
            'message': message
        }))
# Bên client viết vậy (thông báo có 3 dạng. 1 nhắn tin, 2 kết bạn, 3 bình luận , 4 lượt thích)
# const socket = new WebSocket('ws://localhost:8000/ws/notification/');

# socket.onopen = function() {
#     console.log('Connected to the server.');
# };

# socket.onmessage = function(e) {
#     const data = JSON.parse(e.data);
#     console.log('Received message:', data.message);
# };

# socket.onclose = function() {
#     console.log('Disconnected from the server.');
# };

class CommentConsumer(AsyncWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi lại thông báo cho client
        self.send(text_data=json.dumps({
            'message': message
        }))
# code phần client tương tự trên
from channels.generic.websocket import WebsocketConsumer
class OnlineStatusConsumer(WebsocketConsumer):
    consumers = set()  # Set to store all active consumers

    def connect(self):
        self.accept()
        self.consumers.add(self)  # Add the consumer to the set of active consumers

    def disconnect(self, close_code):
        self.consumers.remove(self)  # Remove the consumer from the set of active consumers

    def broadcast_message(self, message):
        for consumer in self.consumers:
            consumer.send(text_data=json.dumps({
                'message': message
            }))
#  bên client

# const socket = new WebSocket('ws://localhost:8000/ws/notification/');

# socket.onopen = function() {
#     console.log('Connected to the server.');
# };

# socket.onmessage = function(e) {
#     const data = JSON.parse(e.data);
#     console.log('Received message:', data.message);
# };

# socket.onclose = function() {
#     console.log('Disconnected from the server.');
# };

from asgiref.sync import async_to_sync 
class VideoCallConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.room_name = 'video_call_group'
        self.room_group_name = 'video_call_group'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_offer(self, event):
        offer = event['offer']
        self.send(text_data=json.dumps({
            'offer': offer
        }))