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
    path('testthu', views.send_offer, name="testthu"),
    path('api/check_login_status', views.check_login_status),
    path('messengerajax/<int:id>/', views.your_ajax_view, name='your-ajax-view'),
    path('createPost',views.createPost, name="createPost"),
    path('editProfile',views.editProfile, name="editProfile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

      



