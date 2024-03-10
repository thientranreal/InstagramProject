
from django.urls import path,re_path
from .consumer import *

ws_urlpatterns=[
    # path("ws/chat/test/", GraphConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<chat_box_name>\w+)/", ChatConsumer.as_asgi()),
    path('ws/notification/', NoftificationConsumer.as_asgi()),
    path('ws/commment/', CommentConsumer.as_asgi()),
    path('ws/onlinestatus/', OnlineStatusConsumer.as_asgi()),
    re_path(r'^ws/video_call/$', VideoCallConsumer.as_asgi()),
]







