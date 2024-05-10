import json
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
from django.utils import timezone
# from django.utils.functional import sync_to_async
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.chat_box_name = self.scope["url_route"]["kwargs"]["chat_box_name"]
        self.group_name = "chat"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        id_user = text_data_json["id_user"]
        id_receiver = text_data_json["id_receiver"]
        user_name = text_data_json["user_name"]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "id_user": id_user,
                "id_receiver": id_receiver,
                "user_name": user_name,
            },
        )
    async def chatbox_message(self, event):
        message = event["message"]
        id_receiver = event["id_receiver"]
        id_user = event["id_user"]
        user_name = event["user_name"]
        # Check if the message is meant for this consumer
        # if id_receiver == self.scope["user"].id:
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "id_user": id_user,
                    "id_receiver": id_receiver,
                    "user_name": user_name,
                }
            )
        )

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.chat_box_name = self.scope["url_route"]["kwargs"]["id"]
        # self.group_name = "groupchat"+self.chat_box_name
        self.group_name = "groupchat"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        id_user = text_data_json["id_user"]
        user_name =text_data_json["user_name"]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "id_user": id_user,
                "user_name": user_name,
            },
        )
    async def chatbox_message(self, event):
        message = event["message"]
        user_name = event["user_name"]
        id_user = event["id_user"]
        # Check if the message is meant for this consumer
        # if id_receiver == self.scope["user"].id:
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "id_user": id_user,
                    "user_name": user_name,
                }
            )
        )


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
        self.group_name = "comment"

        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        comment = text_data_json['comment']
        post_id = text_data_json['post_id']
        username = text_data_json['username']
        avatar = text_data_json['avatar']
        timestamp = text_data_json['timestamp']

        # Gửi lại thông báo cho client
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "comment_message",
                "comment": comment,
                "post_id": post_id,
                "username": username,
                "avatar": avatar,
                "timestamp": timestamp,
            },
        )

    # Receive message from room group.
    async def comment_message(self, event):
        comment = event["comment"]
        post_id = event["post_id"]
        username = event["username"]
        avatar = event["avatar"]
        timestamp = event["timestamp"]
        #send message and username of senter to websocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "comment",
                    "comment": comment,
                    "post_id": post_id,
                    "username": username,
                    "avatar": avatar,
                    "timestamp": timestamp,
                }
            )
        )

class AddFriendConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "addfriend"

        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Xử lý dữ liệu nhận được nếu cần thiết
        text_data_json = json.loads(text_data)
        receive_user = text_data_json['receive_user']
        noidung = text_data_json['noidung']

        # Gửi lại thông báo cho client
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "add_friend_message",
                "receive_user": receive_user,
                "noidung": noidung,
            },
        )

    # Receive message from room group.
    async def add_friend_message(self, event):
        receive_user = event['receive_user']
        noidung = event['noidung']

        #send message and username of senter to websocket
        await self.send(
            text_data=json.dumps(
                {
                    "receive_user": receive_user,
                    "noidung": noidung,
                }
            )
        )
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


class CallConsumer(WebsocketConsumer):
        def connect(self):
            self.group_name = "call"
            self.accept()
            self.send(text_data=json.dumps({
                'type': 'connection',
                'data': {
                    'message': "Connected"
                }
            }))

        def disconnect(self, close_code):
            async_to_sync(self.channel_layer.group_discard)(
                self.my_name,
                self.channel_name
            )

        # Receive message from client WebSocket
        def receive(self, text_data):
            text_data_json = json.loads(text_data)
            eventType = text_data_json['type']

            if eventType == 'login':
                name = text_data_json['data']['name']
                self.my_name = name
                async_to_sync(self.channel_layer.group_add)(
                    self.my_name,
                    self.channel_name
                )
            
            if eventType == 'call':
                name = text_data_json['data']['name']
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
                caller = text_data_json['data']['caller']
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
            self.send(text_data=json.dumps({
                'type': 'call_received',
                'data': event['data']
            }))


        def call_answered(self, event):
            self.send(text_data=json.dumps({
                'type': 'call_answered',
                'data': event['data']
            }))


        def ICEcandidate(self, event):
            self.send(text_data=json.dumps({
                'type': 'ICEcandidate',
                'data': event['data']
            }))
            
class GroupCallConsumer(WebsocketConsumer):
        def connect(self):
            self.group_name = "groupcall"
            self.accept()
            self.send(text_data=json.dumps({
                'type': 'connection',
                'data': {
                    'message': "Connected"
                }
            }))

        def disconnect(self, close_code):
            async_to_sync(self.channel_layer.group_discard)(
                self.my_name,
                self.channel_name
            )

        # Receive message from client WebSocket
        def receive(self, text_data):
            text_data_json = json.loads(text_data)
            eventType = text_data_json['type']

            if eventType == 'login':
                name = text_data_json['data']['id_user']
                self.my_name = name
                async_to_sync(self.channel_layer.group_add)(
                    self.my_name,
                    self.channel_name
                )
            
            # if eventType == 'call':
            #     name = text_data_json['data']['id_group']
            #     async_to_sync(self.channel_layer.group_send)(
            #         name,
            #         {
            #             'type': 'call_received',
            #             'data': {
            #                 'caller': self.my_name,
            #                 'rtcMessage': text_data_json['data']['rtcMessage']
            #             }
            #         }
            #     )
            if eventType == 'call':
            # Kiểm tra xem người gọi có quyền gọi đến nhóm không
                caller = self.my_name
                group_id = text_data_json['data']['id_group']
                if self.check_call_permission(caller, group_id):
                    async_to_sync(self.channel_layer.group_send)(
                        group_id,
                        {
                            'type': 'call_received',
                            'data': {
                                'caller': self.my_name,
                                'rtcMessage': text_data_json['data']['rtcMessage']
                            }
                        }
                    )
                else:
                    self.send(text_data=json.dumps({
                        'type': 'call_error',
                        'data': {
                            'message': "You do not have permission to call this group."
                        }
                    }))

            if eventType == 'answer_call':
                caller = text_data_json['data']['caller']
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
        def check_call_permission(self, caller, group_id):
            # Đây là nơi bạn kiểm tra xem người gọi có quyền gọi đến nhóm không
            # Bạn có thể truy vấn cơ sở dữ liệu hoặc sử dụng logic tùy chỉnh ở đây
            return True  # Trả về True nếu có quyền, False nếu không có quyền
        
        
        
        def call_received(self, event):
            self.send(text_data=json.dumps({
                'type': 'call_received',
                'data': event['data']
            }))


        def call_answered(self, event):
            self.send(text_data=json.dumps({
                'type': 'call_answered',
                'data': event['data']
            }))


        def ICEcandidate(self, event):
            self.send(text_data=json.dumps({
                'type': 'ICEcandidate',
                'data': event['data']
            }))