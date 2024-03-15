from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, get_user_model, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import *
import json
import re

def home(request):
    # Người dùng chưa đăng nhập
    if request.user.is_authenticated is False:
        return redirect("login")
    post = BaiDang.objects.all()
    context = {'posts': post}
    return render(request, 'apps/homepage.html',context)

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
    current_user = request.user.nguoidung
    lienlac = LienLac.objects.filter(goc=current_user)
    context = {'lienlac': lienlac,'current_user': current_user}
    return render(request, 'apps/messenger.html', context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

from django.core import serializers

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
def load_comment(request, id):
    # if request.method == 'GET' and is_ajax(request=request):
        try:
            # item = YourModel.objects.get(id=id)

            comment = BinhLuan.objects.all()
            serialized_binhluan = serializers.serialize('json', comment)
            data = {
                'binhluan':serialized_binhluan,
                'id':id
            }
            return JsonResponse(data)
        except TinNhan.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    # else:
    #     return JsonResponse({'error': 'Invalid request'}, status=400)

def video_call(request, room_name):
    return render(request, 'apps/testthu.html', {'room_name': room_name})

def call_view(request):
    return render(request, 'apps/call.html')

def receive_call_view(request):
    return render(request, 'apps/receive_call.html')

@csrf_exempt  # Vô hiệu hóa CSRF cho các API endpoints
def send_offer(request):
    if request.method == 'GET':
        # Xử lý yêu cầu gọi, tạo offer và gửi nó đến người nhận
        # Truy vấn và xác thực người dùng ở đây (nếu cần)
        offer_data = generate_offer()  # Phương thức tạo offer từ webrtc module
        return JsonResponse({'offer': offer_data})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt  # Vô hiệu hóa CSRF cho các API endpoints
def send_answer(request):
    if request.method == 'POST':
        # Xử lý phản hồi, tạo answer và gửi nó cho người gọi
        # Truy vấn và xác thực người dùng ở đây (nếu cần)
        answer_data = generate_answer()  # Phương thức tạo answer từ webrtc module
        return JsonResponse({'answer': answer_data})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
def generate_offer():
    # Đây là nơi bạn sẽ sử dụng WebRTC API để tạo SDP offer
    # Ví dụ:
    offer = {
        'type': 'offer',
        'sdp': 'SDP offer data'
    }
    return offer

def generate_answer():
    # Đây là nơi bạn sẽ sử dụng WebRTC API để tạo SDP answer
    # Ví dụ:
    answer = {
        'type': 'answer',
        'sdp': 'SDP answer data'
    }
    return answer


def chat_box(request, chat_box_name):
    # we will get the chatbox name from the url
    return render(request, 'apps/chatbox.html', {'chat_box_name': chat_box_name})

# @csrf_exempt
# def send_offer(request):
#     if request.method == 'POST':
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'video_call_group', {
#                 'type': 'send.offer',
#                 'offer': json.loads(request.body),
#             }
#         )
#         return JsonResponse({'status': 'offer sent'})
#     return JsonResponse({'status': 'error'}, status=400)

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


def createPost(request):
    return render(request, 'apps/createPost.html')

def editProfile(request):
    return render(request, 'apps/editProfile.html')