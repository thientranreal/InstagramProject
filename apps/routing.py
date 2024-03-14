
from django.urls import path,re_path
from .consumer import *

ws_urlpatterns=[
    # path("ws/chat/test/", GraphConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<chat_box_name>\w+)/", ChatConsumer.as_asgi()),
    re_path(r'ws/notification/', NoftificationConsumer.as_asgi()),
    re_path(r'ws/commment/', CommentConsumer.as_asgi()),
    re_path(r'ws/onlinestatus/', OnlineStatusConsumer.as_asgi()),
    # re_path(r'ws/videocall/(?P<room_name>\w+)/$', VideoCallConsumer.as_asgi()),
    re_path(r'ws/call/', CallConsumer.as_asgi()),
    path('ws/online-status/', OnlineStatusConsumer.as_asgi()),
]







