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
    path('updatelike/', views.updatelike, name="updatelike"),
    path('loaduserlike/', views.loaduserlike, name="loaduserlike"),
    path('profile', views.getInfoProfile, name="profile"),
    path('messenger', views.messenger, name="messenger"),
    path('create_group', views.create_group, name="create_group"),
    path('delete-contact/', views.delete_contact, name='delete_contact'),
    path('call/', views.call_view, name='call'),
    path('api/check_login_status', views.check_login_status),
    path('messengerajax/<int:id>/', views.load_mess, name='load_mess'),
    path('groupmessengerajax/<int:id>/', views.load_mess_group, name='load_mess_group'),
    path('commentajax/<int:id>/', views.load_comment, name='load_comment'),
    path('editProfile', views.editProfile,name='editProfile'),
    path('edit_profile', views.edit_profile,name='edit_profile'),
    path('createPost', views.createPost,name='createPost'),
    path('create_post', views.create_post,name='create_post'),
    path('editPost/<int:baidang_id>/', views.editPost,name='editPost'),
    path('edit_post/<int:baidang_id>/', views.edit_post,name='edit_post'),
    path('api/comment_post', views.comment_post),
    path('api/save_messenger', views.save_messenger),
    path('api/save_messenger_group', views.save_messenger_group),
    path('call/<int:id>/', views.rendercall, name='rendercall'),
    path('profile_friend/<int:user_id>/', views.profile_friend, name='profile_friend'),
    path('xoa_baidang/<int:baidang_id>/', views.xoa_baidang, name='xoa_baidang'),
    path('add_notification', views.add_notification),
    path('is_read_notification', views.set_isread_notification),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

      



