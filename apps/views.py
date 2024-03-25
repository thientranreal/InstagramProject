from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, get_user_model, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core import serializers
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.core.files import File
from .models import *
import json
import re

def home(request):
    # Người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect("login")

    posts = BaiDang.objects.all()
    for post in posts:
        post.formatted_thoigiandang = format_time_ago(post.thoigiandang)

    context = {'posts': posts}
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
    lienlac = LienLac.objects.filter(goc=current_user)
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
    # Lấy thông tin người dùng hiện tại
    current_user = request.user.nguoidung
    # Lấy danh sách id của các người dùng đã kết bạn với người dùng hiện tại
    friends_ids = BanBe.objects.filter(nguoidung1=current_user).values_list('nguoidung2_id', flat=True)
    # Lấy thông tin của tất cả người dùng trừ người dùng hiện tại đăng nhập và những người dùng đã kết bạn với người dùng hiện tại
    other_users = NguoiDung.objects.exclude(user=current_user.user).exclude(id__in=friends_ids)
    
    # Truyền combined_users vào context
    context = {'other_users': other_users}
    return render(request, 'apps/friend.html', context)

def updatefriend(request):
    nguoidung1 = request.user.nguoidung  # Lấy đối tượng NguoiDung từ user của request
    print(nguoidung1)
    
    data = json.loads(request.body)
    nguoidung2_username = data['userId']  # Giả sử nguoidung2_id được truyền dưới dạng tên người dùng (username)
    print(nguoidung2_username)

    # Tìm nguoidung2 dựa trên tên người dùng
    try:
        nguoidung2 = NguoiDung.objects.get(user__username=nguoidung2_username)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)

    action = data['action']  
    
    if action == 'add':
        friendship = BanBe.objects.create(nguoidung1=nguoidung1, nguoidung2=nguoidung2)
        friendship.save()
        
        return JsonResponse({'message': 'Friendship added successfully'}, status=200)
    
    elif action == 'remove':
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

