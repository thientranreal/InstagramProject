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
    path('profile', views.profile, name="profile"),
    path('messenger', views.messenger, name="messenger"),
    path('chat/<str:chat_box_name>/', views.chat_box, name="chat"),
    path('testthu', views.send_offer, name="testthu"),
    path('api/check_login_status', views.check_login_status)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

      



