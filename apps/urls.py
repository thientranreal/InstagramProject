from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('login', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path('friend', views.friend, name="friend"),
    path('updatefriend/', views.updatefriend, name="updatefriend"),
    path('profile', views.profile, name="profile"),
    path('messenger', views.messenger, name="messenger"),
    path('chat/<str:chat_box_name>/', views.chat_box, name="chat"),
    # path('videocall/<str:room_name>/', views.video_call, name='video_call'),
    path('call/', views.call_view, name='call'),
    # path('receive_call/', views.receive_call_view, name='receive_call'),
    # path('send_offer/', views.send_offer, name='send_offer'),
    # path('send_answer/', views.send_answer, name='send_answer'),
    path('api/check_login_status', views.check_login_status),
    path('messengerajax/<int:id>/', views.load_mess, name='load_mess'),
    path('commentajax/<int:id>/', views.load_comment, name='load_comment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

      



