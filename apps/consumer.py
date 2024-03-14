
import json
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *

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
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi lại thông báo cho client
        await self.send(text_data=json.dumps({
            'message': message
        }))
    pass


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi lại thông báo cho client
        await self.send(text_data=json.dumps({
            'message': message
        }))
# code phần client tương tự trên


from channels.generic.websocket import WebsocketConsumer
class OnlineStatusConsumer(WebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.online_status = True
        await self.update_online_status()

    async def disconnect(self, close_code):
        self.online_status = False
        await self.update_online_status()

    async def update_online_status(self):
        NguoiDung.objects.filter(id=self.user_id).update(is_online=self.online_status)
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('user_id')
        # Xác định người dùng có ID user_id là trực tuyến và gửi tin nhắn thông báo
        # Trong thực tế, bạn cần xử lý việc lưu trạng thái trực tuyến của người dùng và thông báo trạng thái tương ứng
        await self.send(text_data=json.dumps({'status': 'online', 'user_id': user_id}))
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
class CallConsumer(WebsocketConsumer):
        def connect(self):
            self.accept()

            # response to client, that we are connected.
            self.send(text_data=json.dumps({
                'type': 'connection',
                'data': {
                    'message': "Connected"
                }
            }))

        def disconnect(self, close_code):
            # Leave room group
            async_to_sync(self.channel_layer.group_discard)(
                self.my_name,
                self.channel_name
            )

        # Receive message from client WebSocket
        def receive(self, text_data):
            text_data_json = json.loads(text_data)
            # print(text_data_json)

            eventType = text_data_json['type']

            if eventType == 'login':
                name = text_data_json['data']['name']

                # we will use this as room name as well
                self.my_name = name

                # Join room
                async_to_sync(self.channel_layer.group_add)(
                    self.my_name,
                    self.channel_name
                )
            
            if eventType == 'call':
                name = text_data_json['data']['name']
                print(self.my_name, "is calling", name);
                # print(text_data_json)


                # to notify the callee we sent an event to the group name
                # and their's groun name is the name
                async_to_sync(self.channel_layer.group_send)(
                    name,
                    {
                        'type': 'call_received',
                        'data': {
                            'caller': self.my_name,
                            'rtcMessage': text_data_json['data']['rtcMessage']
                        }
                    }
                )

            if eventType == 'answer_call':
                # has received call from someone now notify the calling user
                # we can notify to the group with the caller name
                
                caller = text_data_json['data']['caller']
                # print(self.my_name, "is answering", caller, "calls.")

                async_to_sync(self.channel_layer.group_send)(
                    caller,
                    {
                        'type': 'call_answered',
                        'data': {
                            'rtcMessage': text_data_json['data']['rtcMessage']
                        }
                    }
                )

            if eventType == 'ICEcandidate':

                user = text_data_json['data']['user']

                async_to_sync(self.channel_layer.group_send)(
                    user,
                    {
                        'type': 'ICEcandidate',
                        'data': {
                            'rtcMessage': text_data_json['data']['rtcMessage']
                        }
                    }
                )

        def call_received(self, event):

            # print(event)
            print('Call received by ', self.my_name )
            self.send(text_data=json.dumps({
                'type': 'call_received',
                'data': event['data']
            }))


        def call_answered(self, event):

            # print(event)
            print(self.my_name, "'s call answered")
            self.send(text_data=json.dumps({
                'type': 'call_answered',
                'data': event['data']
            }))


        def ICEcandidate(self, event):
            self.send(text_data=json.dumps({
                'type': 'ICEcandidate',
                'data': event['data']
            }))