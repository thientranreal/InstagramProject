from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, get_user_model, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core import serializers
from django.core.serializers import serialize
from django.db.models import Max, Q, Prefetch
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone
from .models import *
import json
import re

def home(request):
    # Người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect("login")

    # Sắp xếp các BinhLuan theo thời gian tạo
    latest_comments = Prefetch(
        'binhluan_set', 
        queryset=BinhLuan.objects.order_by('-timestamp')
    )

    # Lấy tất cả BaiDang và prefetch 3 BinhLuan mới nhất
    posts = BaiDang.objects.prefetch_related(latest_comments)

    for post in posts:
        post.latest_comments = post.binhluan_set.all()[:3]
        post.latest_comments.reverse()
        for comment in post.latest_comments:
            comment.timestamp = format_time_ago(comment.timestamp)
        post.formatted_thoigiandang = format_time_ago(post.thoigiandang)

    # Hiển thị tin nhắn
    if hasattr(request.user, 'nguoidung'):
        # Lấy các tin nhắn có liên quan tới người dùng hiện tại và tin nhắn mới nhất
        messages_current_user = TinNhan.objects.filter(Q(receiver=request.user.nguoidung) | Q(senter=request.user.nguoidung)).values('senter', 'receiver').annotate(thoigian_moi_nhat=Max('thoigian'))

        # Lấy username và nội dung tin nhắn mới nhất từ mỗi người gửi
        messages = []
        for message in messages_current_user:
            senter_id = message['senter']
            receiver_id = message['receiver']

            # Lấy người dùng dựa theo id
            senter = NguoiDung.objects.get(id=senter_id)
            receiver = NguoiDung.objects.get(id=receiver_id)

            # Nếu người gửi là người dùng hiện tại thì sẽ hiển thị người nhận
            if senter.user.username == request.user.username:
                newestTime = message['thoigian_moi_nhat']
                newestMessage = TinNhan.objects.filter(receiver__id=receiver_id, thoigian=newestTime).first()
                messages.append({'nguoidung': receiver, 'noidung': newestMessage.noidung})
            # Nếu người nhận là người dùng hiện tại thì sẽ hiển thị người gửi
            elif receiver.user.username == request.user.username:
                newestTime = message['thoigian_moi_nhat']
                newestMessage = TinNhan.objects.filter(senter__id=senter_id, thoigian=newestTime).first()
                messages.append({'nguoidung': senter, 'noidung': newestMessage.noidung})

    context = {'posts': posts, 'messages': messages}
    return render(request, 'apps/homepage.html', context)

def signup(request):
    if request.method == 'POST':
        # Lấy giá trị gửi từ client
        data = json.loads(request.body)
        phone_email = data.get('phone_email')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        password = data.get('password')

        # Nếu username đã tồn tại
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': 'error', 
                'message': "This username isn't available. Please try another."
            })

        # Nếu username chưa tồn tại
        else:
            # Nếu trường đầu tiên là email
            if is_email(phone_email):
                # Nếu email đã tồn tại
                if User.objects.filter(email=phone_email).exists():
                    return JsonResponse({
                        'status': 'error', 
                        'message': "This email isn't available. Please try another."
                    })
                else:
                    # Nếu phone_email là email, tạo người dùng với email
                    # Tạo user mới
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=firstname,
                        last_name=lastname,
                        email=phone_email
                    )
                    # Tạo người dùng mới
                    NguoiDung.objects.create(user=user)

                    # Đăng nhập với người dùng vừa signup
                    auth_login(request, user)
                    return JsonResponse({'status': 'ok'})

            # Nếu trường đầu tiên là số điện thoại
            elif is_phone_number(phone_email):
                # Nếu số điện thoại đã tồn tại
                if NguoiDung.objects.filter(phone=phone_email).exists():
                    return JsonResponse({
                        'status': 'error', 
                        'message': "This phone number isn't available. Please try another."
                    })
                else:
                    # Nếu phone_email là số điện thoại, tạo người dùng không có email
                    # Tạo user mới
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=firstname,
                        last_name=lastname
                    )
                    # Tạo người dùng mới
                    NguoiDung.objects.create(user=user, phone=phone_email)

                    # Đăng nhập với người dùng vừa signup
                    auth_login(request, user)
                    return JsonResponse({'status': 'ok'})
            
                    
    return render(request, 'apps/signup.html')

def check_login_status(request):
    # Kiểm tra xem người dùng nào đang đăng nhập không
    if request.user.is_authenticated:
        return JsonResponse({'status': 'login'})
    else:
        return JsonResponse({'status': 'not login'})

def login(request):
    if request.method == 'POST':
        # Lấy giá trị gửi từ client
        data = json.loads(request.body)
        identifier = data.get('identifier')
        password = data.get('password')

        # Thử xác thực bằng username
        user = authenticate(username=identifier, password=password)
        # Nếu tài khoản tồn tại thì đăng nhập và gửi status là ok
        if user is not None:
            auth_login(request, user)
            return JsonResponse({'status': 'ok'})
        
        if user is None:
            try:
                # Thử xác thực bằng email
                user = User.objects.get(email=identifier)
                user = authenticate(username=user.username, password=password)
                # Nếu tài khoản tồn tại thì đăng nhập và gửi status là ok
                if user is not None:
                    auth_login(request, user)
                    return JsonResponse({'status': 'ok'})
            except User.DoesNotExist:
                pass

        if user is None:
            try:
                # Thử xác thực bằng số điện thoại
                user = NguoiDung.objects.get(phone=identifier).user
                user = authenticate(username=user.username, password=password)
                # Nếu tài khoản tồn tại thì đăng nhập và gửi status là ok
                if user is not None:
                    auth_login(request, user)
                    return JsonResponse({'status': 'ok'})
            except NguoiDung.DoesNotExist:
                pass

        if user is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Sorry, your password was incorrect. Please double-check your password.'
            })
        
    return render(request, 'apps/login.html')

def profile(request):
    return render(request, 'apps/profile.html')

def messenger(request):
    # current_user = request.user.nguoidung
    current_user = request.user.nguoidung
    lienlac = LienLac.objects.filter(Q(goc=current_user) | Q(dich=current_user))
    context = {'lienlac': lienlac,'current_user': current_user}
    return render(request, 'apps/messenger.html', context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def load_mess(request, id):
    # if request.method == 'GET' and is_ajax(request=request):
        try:
            # item = YourModel.objects.get(id=id)

            tinnhan = TinNhan.objects.all()
            # tinnhan = TinNhan.objects.filter(senter=id)

            serialized_tinnhan = serializers.serialize('json', tinnhan)
            data = {
                'tinnhan':serialized_tinnhan,
                'id':id
            }
            return JsonResponse(data)
        except TinNhan.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    # else:
    #     return JsonResponse({'error': 'Invalid request'}, status=400)

def format_time_ago(timestamp):
    now = datetime.now()
    time_difference = now - timestamp.replace(tzinfo=None)

    if time_difference < timedelta(minutes=1):
        return "Just now"
    elif time_difference < timedelta(hours=1):
        return f"{int(time_difference.total_seconds() // 60)} minutes ago"
    elif time_difference < timedelta(days=1):
        return f"{int(time_difference.total_seconds() // 3600)} hours ago"
    elif time_difference < timedelta(weeks=1):
        return f"{int(time_difference.total_seconds() // 86400)} days ago"
    else:
        return timestamp.strftime("%Y-%m-%d %H:%M")

def load_comment(request, id):
    try:
        # Lấy tất cả các bình luận cho bài đăng có id tương ứng
        comments = BinhLuan.objects.filter(baidang_id=id)
        # Tạo một danh sách chứa thông tin bình luận và avatar
        serialized_comments = []
        for comment in comments:
            serialized_comment = {
                'comment': {
                    'id': comment.id,
                    'noidungbl': comment.noidungbl,
                    'timestamp': format_time_ago(comment.timestamp)
                },
                'user_info':{
                    'id': comment.nguoidung_id,
                    'avatar': comment.nguoidung.avatar.url if comment.nguoidung.avatar else 'media/download.png',  # Khởi tạo avatar là None, nếu người dùng không tồn tại hoặc không có avatar
                    'username': comment.nguoidung.user.username
                }
            }
            serialized_comments.append(serialized_comment)

        # Chuyển đổi danh sách serialized_comments thành JSON
        data = {
            'binhluan': serialized_comments,
            'id': id
        }
        return JsonResponse(data)
    except BinhLuan.DoesNotExist:
        return JsonResponse({'error': 'Comments not found'}, status=404)

def video_call(request, room_name):
    return render(request, 'apps/testthu.html', {'room_name': room_name})

def call_view(request):
    return render(request, 'apps/call.html')


def chat_box(request, chat_box_name):
    # we will get the chatbox name from the url
    return render(request, 'apps/chatbox.html', {'chat_box_name': chat_box_name})

# Hàm kiểm tra email
def is_email(value):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, value) is not None

# Hàm kiểm tra số điện thoại
def is_phone_number(phone_number):
    phone_regex = r'^(03|05|07|08|09|01[2|6|8|9])+([0-9]{8})\b'
    return re.match(phone_regex, phone_number) is not None

def friend(request):
    current_user = request.user.nguoidung

    if request.method == 'POST':
        data = json.loads(request.body)
        search_users = User.objects.filter(username__icontains=data['searchData'])
        if search_users.exists():
            search_user_ids = [user.id for user in search_users] 
            
            other_users = NguoiDung.objects.filter(id__in=search_user_ids).exclude(
                Q(id=current_user.id) | 
                Q(id__in=BanBe.objects.filter(nguoidung1_id=current_user.id).values_list('nguoidung2_id', flat=True)) | 
                Q(id__in=BanBe.objects.filter(nguoidung2_id=current_user.id).values_list('nguoidung1_id', flat=True)) 
            ).values('avatar', 'user__username', 'user__first_name', 'user__last_name', 'sobanbe')
            
            sender_friend_ids = BanBe.objects.filter(nguoidung1_id=current_user.id, nguoidung2_id__in=search_user_ids, is_banbe=False).values('nguoidung2__avatar', 'nguoidung2__user__username', 'nguoidung2__user__first_name', 'nguoidung2__user__last_name', 'nguoidung2__sobanbe')
            
            receiver_friend_ids = BanBe.objects.filter(nguoidung2_id=current_user.id, nguoidung1_id__in=search_user_ids, is_banbe=False).values('nguoidung1__avatar', 'nguoidung1__user__username', 'nguoidung1__user__first_name', 'nguoidung1__user__last_name', 'nguoidung1__sobanbe')
            
            friend_ids = BanBe.objects.filter(Q(nguoidung1_id=current_user.id, nguoidung2_id__in=search_user_ids) | Q(nguoidung2_id=current_user.id, nguoidung1_id__in=search_user_ids), is_banbe=True).values_list('nguoidung1_id', 'nguoidung2_id')
            all_friend_ids = set()
            for friend in friend_ids:
                all_friend_ids.add(friend[0])
                all_friend_ids.add(friend[1])
            all_friend_ids.discard(current_user.id)
            
            friends = NguoiDung.objects.filter(id__in=all_friend_ids).values('avatar', 'user__username', 'user__first_name', 'user__last_name', 'sobanbe')
            
            other_users_data = list(other_users)
            sender_friend_ids_data = list(sender_friend_ids)
            receiver_friend_ids_data = list(receiver_friend_ids)
            friends_data = list(friends)

            return JsonResponse({'other_users': other_users_data, 
                                'sender_friend_ids': sender_friend_ids_data, 
                                'receiver_friend_ids': receiver_friend_ids_data, 
                                'friends': friends_data})
    else:
        # Sử dụng truy vấn mặc định khi không có yêu cầu POST
        other_users = NguoiDung.objects.exclude(
            Q(id=current_user.id) | 
            Q(id__in=BanBe.objects.filter(nguoidung1_id=current_user.id).values_list('nguoidung2_id', flat=True)) | 
            Q(id__in=BanBe.objects.filter(nguoidung2_id=current_user.id).values_list('nguoidung1_id', flat=True))
        )
        # Lấy tất cả bạn của người dùng hiện tại (người gửi lời mời kết bạn)
        sender_friend_ids = BanBe.objects.filter(nguoidung1_id=current_user.id, is_banbe=False)
        # Lấy tất cả bạn của người dùng hiện tại (người nhận lời mời kết bạn) 
        receiver_friend_ids = BanBe.objects.filter(nguoidung2_id=current_user.id, is_banbe=False)
        # Lấy tất cả bạn của người dùng hiện tại
        friend_ids = BanBe.objects.filter(Q(nguoidung1_id=current_user.id) | Q(nguoidung2_id=current_user.id), is_banbe=True)
        all_friend_ids = []
        for friend in friend_ids:
            if friend.nguoidung1_id == current_user.id:
                all_friend_ids.append(friend.nguoidung2_id)
            else:
                all_friend_ids.append(friend.nguoidung1_id)
        friends = [NguoiDung.objects.get(id=user_id) for user_id in all_friend_ids]
        context = {'other_users': other_users, 'sender_friend_ids': sender_friend_ids, 'receiver_friend_ids': receiver_friend_ids, 'friends': friends}
        return render(request, 'apps/friend.html', context)

def updatefriend(request):
    nguoidung1 = request.user.nguoidung  
    if request.method == 'POST':
        data = json.loads(request.body)
        nguoidung2_username = data['userId']  
        action = data['action']  

        try:
            nguoidung2 = NguoiDung.objects.get(user__username=nguoidung2_username)
        except NguoiDung.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        
        if action == 'add':
            friendship = BanBe.objects.create(nguoidung1=nguoidung1, nguoidung2=nguoidung2)
            friendship.thoigian = timezone.now()  # Update time
            friendship.save()
            return JsonResponse({'message': 'Friendship added successfully'}, status=200)
        elif action == 'remove':
            friendship = BanBe.objects.get(Q(nguoidung1=nguoidung2, nguoidung2=nguoidung1) | Q(nguoidung1=nguoidung1, nguoidung2=nguoidung2))
            friendship.delete()
            return JsonResponse({'message': 'Friendship removed successfully'}, status=200)
        elif action == 'cancel':
            friendship = BanBe.objects.get(nguoidung1=nguoidung1, nguoidung2=nguoidung2)
            friendship.delete()
            return JsonResponse({'message': 'Friendship removed successfully'}, status=200)
        elif action == 'accept':
            friendship = BanBe.objects.get(nguoidung1=nguoidung2, nguoidung2=nguoidung1)
            friendship.is_banbe = True
            friendship.thoigian = timezone.now()  # Update time
            friendship.save()
            return JsonResponse({'message': 'Friendship accepted successfully'}, status=200)
        elif action == 'refuse':
            friendship = BanBe.objects.get(nguoidung1=nguoidung2, nguoidung2=nguoidung1)
            friendship.delete()
            return JsonResponse({'message': 'Friendship removed successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

def editProfile(request):
    current_user = request.user.nguoidung
    return render(request, 'apps/editProfile.html',{'nguoi_dung': current_user})

def createPost(request):
    current_user = request.user.nguoidung
    return render(request, 'apps/createPost.html',{'nguoi_dung': current_user})


def get_admin_nguoidung():
    try:
        admin_user = User.objects.filter(is_staff=True, is_superuser=True).first()  # Lấy người dùng đầu tiên có is_staff và is_superuser là True
        if admin_user:
            nguoidung = NguoiDung.objects.get(user=admin_user)  # Lấy thông tin người dùng tương ứng
            return nguoidung
        else:
            return None  # Trả về None nếu không tìm thấy người dùng admin
    except NguoiDung.DoesNotExist:
        return None  # Xử lý trường hợp không tìm thấy thông tin người dùng tương ứng
    
def getInfoProfile(request):
    current_user = request.user.nguoidung
    # Truyền dữ liệu nguoi_dungs vào template profile.html
    danh_sach_baidang = BaiDang.objects.filter(nguoidung=current_user)
    so_luong_baidang = danh_sach_baidang.count()
    context ={'nguoi_dung': current_user,'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': so_luong_baidang}
    if so_luong_baidang <=0:
        context ={'nguoi_dung': current_user,'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': 0}
    return render(request, 'apps/profile.html', context)


def create_post(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ request
        noidung = request.POST.get('noidung')
        hinhanh_url = request.FILES['hinhanh_url']  # Đã cung cấp URL hình ảnh trong template
        # Tạo một bài đăng mới
        baidang = BaiDang.objects.create(
            nguoidung=request.user.nguoidung,  # Sử dụng người dùng hiện tại đang đăng nhập
            noidung=noidung,
            thoigiandang=datetime.now(),
            tongluotthich=0,
            tongluotbinhluan=0,
        )
        baidang.hinhanh=hinhanh_url
        baidang.save()

        # Chuyển hướng người dùng đến trang khác hoặc thông báo thành công
        return redirect('home')  # Chuyển hướng về trang chủ sau khi chia sẻ thành công
    else:
        # Xử lý logic khi yêu cầu không phải là POST
        pass


def edit_profile(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action']== 'submit':
                current_user = request.user
                # Lấy dữ liệu từ request
                mota = request.POST.get('mota')
                hinhanh_url = request.FILES['hinhanh_url']  # Đã cung cấp URL hình ảnh trong template
                ngaysinh=request.POST.get('ngaysinh')
                phone=request.POST.get('phone')
                gioitinh=request.POST.get('gioitinh')


                nguoidung1=NguoiDung.objects.get(user=current_user)
                nguoidung1.avatar=hinhanh_url
                nguoidung1.save()
                # Tạo một bài đăng mới
                nguoidung = NguoiDung.objects.filter(user=current_user).update(
                    ngaysinh=ngaysinh,      
                    phone=phone,       
                    gioitinh=gioitinh,  
                    mota=mota 
                )

                # Chuyển hướng người dùng đến trang khác hoặc thông báo thành công
                return redirect('profile')  # Chuyển hướng về trang chủ sau khi chia sẻ thành công
    else:
        # Xử lý logic khi yêu cầu không phải là POST
        pass

def comment_post(request):
    # Thêm comment vào bài đăng
    if request.method == 'POST':
        # Lấy giá trị gửi từ client
        data = json.loads(request.body)
        post_id = data.get('post_id')
        noidungbl = data.get('comment')
        
        # Lấy bài đăng và người dùng
        baidang = BaiDang.objects.get(id=post_id)
        nguoidung = request.user.nguoidung

        # Tạo một BinhLuan mới
        binhluan_moi = BinhLuan.objects.create(
            baidang=baidang,
            nguoidung=nguoidung,
            noidungbl=noidungbl
        )

        # Lưu BinhLuan mới
        binhluan_moi.save()
        # Format lại thời gian
        formatted_timestamp = format_time_ago(binhluan_moi.timestamp)

        return JsonResponse({
                                'status': 'ok',
                                'timestamp': formatted_timestamp
                            })

    # Lấy comment từ bài đăng
    elif request.method == 'GET':
        postId = request.GET.get('postId', '')

        # Lấy đối tượng BaiDang dựa trên postId
        baidang = BaiDang.objects.get(id=postId)
        # Kết quả bình luận
        binhluan_data = []

        # Lấy tất cả BinhLuan của BaiDang
        binhluan_list = BinhLuan.objects.filter(baidang=baidang).order_by('timestamp')

        # Chuyển đổi binhluan_list thành danh sách các dictionary
        for binhluan in binhluan_list:
            # Format lại thời gian
            formatted_timestamp = format_time_ago(binhluan.timestamp)

            binhluan_data.append({
                'noidungbl': binhluan.noidungbl,
                'username': binhluan.nguoidung.user.username,
                'avatar': binhluan.nguoidung.avatar.url if binhluan.nguoidung.avatar else None,
                'timestamp': formatted_timestamp
            })
            
        return JsonResponse({'binhluan': binhluan_data})



