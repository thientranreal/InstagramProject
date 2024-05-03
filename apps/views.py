from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, logout, get_user_model, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core import serializers
from django.core.serializers import serialize
from django.db.models import Max, Q, Prefetch, Count
from datetime import *
from django.shortcuts import redirect, get_object_or_404
from django.http import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone
from .models import *
import json
import re

def home(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if hasattr(request.user, 'nguoidung'):
        ban_be = BanBe.objects.filter(
            Q(nguoidung1__user=request.user) | Q(nguoidung2__user=request.user), 
            is_banbe=True
        )
        ban_be_ids = [bb.nguoidung2.id if bb.nguoidung1.user == request.user else bb.nguoidung1.id for bb in ban_be]

        latest_comments = Prefetch(
            'binhluan_set', 
            queryset=BinhLuan.objects.order_by('-timestamp')
        )

        # Lấy danh sách bài đăng
        posts = BaiDang.objects.filter(
            Q(nguoidung__user=request.user) | Q(nguoidung__id__in=ban_be_ids)
        ).prefetch_related(latest_comments)

        # Kiểm tra xem người dùng đã like bài đăng đó chưa và thêm biến 'liked' vào mỗi bài đăng
        for post in posts:
            post.latest_comments = post.binhluan_set.all()[:3]  
            for comment in post.latest_comments:
                comment.timestamp = format_time_ago(comment.timestamp)
            post.formatted_thoigiandang = format_time_ago(post.thoigiandang)

            # Kiểm tra xem người dùng đã thích bài đăng đó chưa
            post.liked = LikeBaiDang.objects.filter(baidang=post, nguoidung=request.user.nguoidung).exists()

        messages = []

        messages_current_user = TinNhan.objects.filter(
            Q(receiver=request.user.nguoidung) | Q(senter=request.user.nguoidung)
        ).values('senter', 'receiver').annotate(thoigian_moi_nhat=Max('thoigian'))

        for message in messages_current_user:
            senter_id = message['senter']
            receiver_id = message['receiver']

            senter = NguoiDung.objects.get(id=senter_id)
            receiver = NguoiDung.objects.get(id=receiver_id)

            if senter.user.username == request.user.username:
                newestTime = message['thoigian_moi_nhat']
                newestMessage = TinNhan.objects.filter(receiver__id=receiver_id, thoigian=newestTime).first()
                messages.append({'nguoidung': receiver, 'noidung': newestMessage.noidung})
            elif receiver.user.username == request.user.username:
                newestTime = message['thoigian_moi_nhat']
                newestMessage = TinNhan.objects.filter(senter__id=senter_id, thoigian=newestTime).first()
                messages.append({'nguoidung': senter, 'noidung': newestMessage.noidung})
    else:
        logout(request)
        return redirect("login")

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

def is_email(value):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, value) is not None

def is_phone_number(phone_number):
    phone_regex = r'^(03|05|07|08|09|01[2|6|8|9])+([0-9]{8})\b'
    return re.match(phone_regex, phone_number) is not None

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

def messenger(request):
    if not request.user.is_authenticated:
        return redirect("login")
    # current_user = request.user.nguoidung
    current_user = request.user.nguoidung
    lienlac = BanBe.objects.filter(Q(nguoidung1=current_user) | Q(nguoidung2=current_user))
    
    admin_groups = Nhom.objects.filter(admin=current_user)
    member_groups = Nhom.objects.filter(nguoidung=current_user)
    
    nhoms = (admin_groups | member_groups).distinct()
    context = {'lienlac': lienlac,'current_user': current_user,'nhoms':nhoms}
    return render(request, 'apps/messenger.html', context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def load_mess(request, id):
    # if request.method == 'GET' and is_ajax(request=request):
        try:
            # item = YourModel.objects.get(id=id)
            # tinnhan = TinNhan.objects.all()
            tinnhan = TinNhan.objects.filter(Q(senter=id,receiver=request.user.id) | Q(senter=request.user.id, receiver=id)).order_by('thoigian')

            serialized_tinnhan = serializers.serialize('json', tinnhan)
            data = {
                'tinnhan':serialized_tinnhan,
                'id':id
            }
            return JsonResponse(data)
        except TinNhan.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)

def load_mess_group(request, id):
    # if request.method == 'GET' and is_ajax(request=request):
        try:            
            nhom = Nhom.objects.get(id=id)
            tinnhan = TinNhanNhom.objects.filter(nhom=nhom).select_related('sender').order_by('thoigian')
                
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

def save_messenger(request):
    # Thêm comment vào bài đăng
    if request.method == 'POST':
        # Lấy giá trị gửi từ client
        data = json.loads(request.body)
        message = data.get('message') 
        id_user = data.get('id_user') 
        id_receiver = data.get('id_receiver') 
        
        user = NguoiDung.objects.get(id=id_user)
        receiver = NguoiDung.objects.get(id=id_receiver)

        tinnhan = TinNhan.objects.create(
            senter=user,
            receiver=receiver,
            noidung=message,
            thoigian=timezone.now()  
        )
        tinnhan.save()
        
        # lienlac, created = BanBe.objects.get_or_create(Q(nguoidung1=user, nguoidung2=receiver) | Q(nguoidung1=receiver, nguoidung2=user))
        # lienlac.lastmess = message
        # lienlac.thoigiancuoi = timezone.now()
        # lienlac.save()

        return JsonResponse({'status': 'ok'})
    
def save_messenger_group(request):
    # Thêm comment vào bài đăng
    if request.method == 'POST':
        # Lấy giá trị gửi từ client
        data = json.loads(request.body)
        message = data.get('message') 
        id_user = data.get('id_user') 
        # id_receiver = data.get('id_receiver') 
        id_nhom = data.get('id_nhom')
        # k can user_name
        
        user = NguoiDung.objects.get(id=id_user)
        nhom = Nhom.objects.get(id=id_nhom)
        # receiver = NguoiDung.objects.get(id=id_receiver)

        tinnhannhom = TinNhanNhom.objects.create(
            nhom=nhom,
            sender=user,
            noidung=message,
            thoigian=timezone.now()  
        )
        tinnhannhom.save()
        
        # lienlac, created = BanBe.objects.get_or_create(Q(nguoidung1=user, nguoidung2=receiver) | Q(nguoidung1=receiver, nguoidung2=user))
        # lienlac.lastmess = message
        # lienlac.thoigiancuoi = timezone.now()
        # lienlac.save()

        return JsonResponse({'status': 'ok'})

def video_call(request, room_name):
    return render(request, 'apps/testthu.html', {'room_name': room_name})

def call_view(request):
    return render(request, 'apps/call.html')

def rendercall(request,id):
    return render(request, 'apps/call.html',{'id':id})

def delete_contact(request):

    data = json.loads(request.body)
    id_user = data.get('id_user') 
    id_receiver = data.get('id_receiver') 
    
    user = NguoiDung.objects.get(id=id_user)
    receiver = NguoiDung.objects.get(id=id_receiver)

    lienlac = BanBe.objects.get_or_create(Q(nguoidung1=user, nguoidung2=receiver) | Q(nguoidung1=receiver, nguoidung2=user))
    lienlac.delete()

    return JsonResponse({'status': 'ok'})

def create_group(request):
    if request.method == 'POST':
        tennhom = request.POST.get('tennhom')
        tennhom = request.POST.get('tennhom')
        selectedmembers = request.POST.getlist('danhsach')
        selected_members_ids = '2,3'
        selected_members_ids_list = selected_members_ids.split(',')

        # Lấy người dùng hiện tại
        current_user = request.user.nguoidung

        # Tạo nhóm mới
        new_group = Nhom.objects.create(name=tennhom, admin=current_user)
        
        for i in selected_members_ids_list:
            selected_members = NguoiDung.objects.filter(id=i)
            new_group.nguoidung.add(*selected_members)        
        # Lưu lại nhóm
        new_group.save()
           

    return redirect('messenger')

def friend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    current_user = request.user.nguoidung
    if request.method == 'POST':
        data = json.loads(request.body)
        search_users = User.objects.filter(username__icontains=data['searchData'])
        if search_users.exists():
            search_user_ids = [user.nguoidung.id for user in search_users] 

            other_users = NguoiDung.objects.filter(id__in=search_user_ids).exclude(
                Q(id=current_user.id) | 
                Q(id__in=BanBe.objects.filter(nguoidung1_id=current_user.id).values_list('nguoidung2_id', flat=True)) | 
                Q(id__in=BanBe.objects.filter(nguoidung2_id=current_user.id).values_list('nguoidung1_id', flat=True)) 
            )
            
            sender_friend_ids = BanBe.objects.filter(
                nguoidung1_id=current_user.id, 
                nguoidung2_id__in=search_user_ids, 
                is_banbe=False
            )

            receiver_friend_ids = BanBe.objects.filter(
                nguoidung2_id=current_user.id, 
                nguoidung1_id__in=search_user_ids, 
                is_banbe=False
            )

            friend_ids = BanBe.objects.filter(
                Q(nguoidung1_id=current_user.id, nguoidung2_id__in=search_user_ids) | 
                Q(nguoidung2_id=current_user.id, nguoidung1_id__in=search_user_ids), 
                is_banbe=True
            )
            all_friend_ids = set()
            for friend in friend_ids:
                all_friend_ids.add(friend.nguoidung1_id)
                all_friend_ids.add(friend.nguoidung2_id)
            all_friend_ids.discard(current_user.id)
            
            friends = NguoiDung.objects.filter(id__in=all_friend_ids)
            
            return JsonResponse({
                'other_users': list(other_users.values('id', 'avatar', 'user__username', 'user__first_name', 'user__last_name')), 
                'sender_friend_ids': list(sender_friend_ids.values('nguoidung2__id', 'nguoidung2__avatar', 'nguoidung2__user__username', 'nguoidung2__user__first_name', 'nguoidung2__user__last_name')), 
                'receiver_friend_ids': list(receiver_friend_ids.values('nguoidung1__id', 'nguoidung1__avatar', 'nguoidung1__user__username', 'nguoidung1__user__first_name', 'nguoidung1__user__last_name')), 
                'friends': list(friends.values('id', 'avatar', 'user__username', 'user__first_name', 'user__last_name'))
            })
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
            return JsonResponse({'message': 'Friendship cancel successfully'}, status=200)
        elif action == 'accept':
            friendship = BanBe.objects.get(nguoidung1=nguoidung2, nguoidung2=nguoidung1)
            friendship.is_banbe = True
            friendship.thoigian = timezone.now()  # Update time
            friendship.save()
            return JsonResponse({'message': 'Friendship accepted successfully'}, status=200)
        elif action == 'refuse':
            friendship = BanBe.objects.get(nguoidung1=nguoidung2, nguoidung2=nguoidung1)
            friendship.delete()
            return JsonResponse({'message': 'Friendship refuse successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

def profile(request):
    return render(request, 'apps/profile.html')

def editProfile(request):
    current_user = request.user.nguoidung
    ngay_sinh_formatted = current_user.ngaysinh.strftime('%Y-%m-%d') if current_user.ngaysinh else None
    return render(request, 'apps/editProfile.html',{'nguoi_dung': current_user, 'ngay_sinh_formatted': ngay_sinh_formatted})

def edit_profile(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action']== 'submit':
                current_user = request.user
                # Lấy dữ liệu từ request
                mota = request.POST.get('mota')
                ngaysinh=request.POST.get('ngaysinh')
                phone=request.POST.get('phone')
                gioitinh=request.POST.get('gioitinh')

                nguoidung1=NguoiDung.objects.get(user=current_user)
                if 'hinhanh_url' in request.FILES:
                    hinhanh_url = request.FILES['hinhanh_url']
                    nguoidung1.avatar = hinhanh_url
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

def profile_friend(request, user_id):
    if not request.user.is_authenticated:
        return redirect("login")
    current_user = request.user.nguoidung
    nguoi_dung = NguoiDung.objects.get(pk=user_id)
    if current_user.id == nguoi_dung.id:
        return getInfoProfile(request)
    else: 
        danh_sach_baidang = BaiDang.objects.filter(nguoidung=nguoi_dung)
        so_luong_baidang = danh_sach_baidang.count()
        context = {'nguoi_dung': nguoi_dung, 'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': so_luong_baidang}
        if so_luong_baidang <= 0:
            context = {'nguoi_dung': nguoi_dung, 'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': 0}
        return render(request, 'apps/profile.html', context)

def createPost(request):
    current_user = request.user.nguoidung
    return render(request, 'apps/createPost.html',{'nguoi_dung': current_user})

def create_post(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ request
        noidung = request.POST.get('noidung')
        if 'hinhanh_url' in request.FILES:
            hinhanh_url = request.FILES['hinhanh_url']
        else:
            hinhanh_url = None
        # Tạo một bài đăng mới
        baidang = BaiDang.objects.create(
            nguoidung=request.user.nguoidung,  # Sử dụng người dùng hiện tại đang đăng nhập
            noidung=noidung,
            thoigiandang=datetime.now(),
        )
        baidang.hinhanh=hinhanh_url
        baidang.save()

        # Chuyển hướng người dùng đến trang khác hoặc thông báo thành công
        return redirect('home')  # Chuyển hướng về trang chủ sau khi chia sẻ thành công
    else:
        # Xử lý logic khi yêu cầu không phải là POST
        pass

def editPost(request, baidang_id):
    current_user = request.user.nguoidung
    baidang = get_object_or_404(BaiDang, pk=baidang_id)
    return render(request, 'apps/editPost.html',{'nguoi_dung': current_user,'baidang':baidang})

def edit_post(request, baidang_id):
    # Lấy bài đăng từ cơ sở dữ liệu hoặc trả về 404 nếu không tìm thấy
    baidang = get_object_or_404(BaiDang, pk=baidang_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ request
        noidung = request.POST.get('noidung')
        baidang.noidung = noidung
        
        # Kiểm tra và cập nhật hình ảnh nếu có
        if 'hinhanh_url' in request.FILES:
            hinhanh_url = request.FILES['hinhanh_url']
            baidang.hinhanh = hinhanh_url

        # Lưu các thay đổi vào cơ sở dữ liệu
        baidang.save()

        # Chuyển hướng người dùng đến trang khác hoặc thông báo thành công
        return redirect('profile')
    else:
        # Xử lý logic khi yêu cầu không phải là POST
        pass
  
def xoa_baidang(request, baidang_id):
    try:
        # Lấy bài đăng từ cơ sở dữ liệu
        baidang = BaiDang.objects.get(id=baidang_id)
    except BaiDang.DoesNotExist:
        # Trả về 404 nếu không tìm thấy bài đăng
        return HttpResponseNotFound()

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'xoa':
            # Xóa bài đăng
            baidang.delete()
            
            # Chuyển hướng người dùng đến một trang nào đó sau khi xóa thành công
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            # Trả về lỗi 400 Bad Request nếu action không hợp lệ
            return HttpResponseBadRequest("Yêu cầu không hợp lệ")
    else:
        # Nếu yêu cầu không phải từ phương thức POST, trả về 405 Method Not Allowed
        return HttpResponseNotAllowed(['POST'])

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

def updatelike(request):
    if request.method == 'POST':
        nguoidung = request.user.nguoidung
        data = json.loads(request.body)
        idPost = data['idPost']  
        action = data['action']

        try:
            baidang = BaiDang.objects.get(id=idPost)
        except BaiDang.DoesNotExist:
            return JsonResponse({'error': 'BaiDang not found'}, status=404)

        if action == 'like':
            LikeBaiDang.objects.create(baidang=baidang, nguoidung=nguoidung).save()
            return JsonResponse({'message': 'Like successfully'}, status=200)
        elif action == 'remove':
            # Kiểm tra xem người dùng đã like bài đăng này trước đó không
            try:
                like = LikeBaiDang.objects.get(baidang=baidang, nguoidung=nguoidung)
            except LikeBaiDang.DoesNotExist:
                return JsonResponse({'error': 'You have not liked this post yet'}, status=400)
            # Xóa lượt thích khỏi cơ sở dữ liệu
            like.delete()
            return JsonResponse({'message': 'Like removed successfully'}, status=200)

    # Trả về lỗi nếu yêu cầu không phải là POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def loaduserlike(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_post = data.get('idPost')
        current_user_id = request.user.nguoidung.id
        like_users_info = NguoiDung.objects.filter(likebaidang__baidang__id=id_post).values(
            'id', 'avatar', 'user__username', 'user__first_name', 'user__last_name')
        
        # Xét trạng thái bạn bè của các người dùng đã thích bài đăng
        for user_info in like_users_info:
            is_friend = False
            user_id = user_info['id']
            
            # Kiểm tra xem người dùng có phải là người dùng hiện tại không
            if user_id == current_user_id:
                is_friend = "self"
            
            # Kiểm tra nếu là bạn bè
            if BanBe.objects.filter(Q(nguoidung1_id=current_user_id, nguoidung2_id=user_id, is_banbe=True) |
                                     Q(nguoidung1_id=user_id, nguoidung2_id=current_user_id, is_banbe=True)).exists():
                is_friend = True
            
            # Kiểm tra nếu người dùng đã gửi lời mời kết bạn
            elif BanBe.objects.filter(nguoidung1_id=current_user_id, nguoidung2_id=user_id, is_banbe=False).exists():
                is_friend = "pending_sender"
            
            # Kiểm tra nếu người dùng đã nhận lời mời kết bạn
            elif BanBe.objects.filter(nguoidung1_id=user_id, nguoidung2_id=current_user_id, is_banbe=False).exists():
                is_friend = "pending_receiver"
            
            # Lưu trạng thái bạn bè vào thông tin người dùng
            user_info['friendStatus'] = is_friend
        
        return JsonResponse({'likeUsers': list(like_users_info)})
    
    return JsonResponse({'error': 'Invalid request'})

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
    if not request.user.is_authenticated:
        return redirect("login")
    current_user = request.user.nguoidung
    # Truyền dữ liệu nguoi_dungs vào template profile.html
    danh_sach_baidang = BaiDang.objects.filter(nguoidung=current_user)
    so_luong_baidang = danh_sach_baidang.count()
    ngay_sinh_formatted = current_user.ngaysinh.strftime('%Y-%m-%d') if current_user.ngaysinh else None
    context ={'nguoi_dung': current_user,'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': so_luong_baidang, 'edit':1, 'ngay_sinh_formatted': ngay_sinh_formatted}
    if so_luong_baidang <=0:
        context ={'nguoi_dung': current_user,'danh_sach_baidang': danh_sach_baidang, 'so_luong_baidang': 0, 'edit':1, 'ngay_sinh_formatted': ngay_sinh_formatted}
    return render(request, 'apps/profile.html', context)

def add_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        noidung = data.get('noidung')
        thong_bao_moi = ThongBao.objects.create(nguoidung=request.user.nguoidung, noidung=noidung, is_read=False)
        thong_bao_moi.save()
        
        return JsonResponse({'status': 'ok'})
    
def set_isread_notification(request):
    if request.method == 'GET':
        # người dùng hiện tại đọc hết tin nhắn
        ThongBao.objects.filter(nguoidung__user=request.user).update(is_read=True)
        return JsonResponse({'status': 'ok'})

def loadfriend(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('id')
        friends = BanBe.objects.filter(
            Q(nguoidung1=user_id, is_banbe=True) | Q(nguoidung2=user_id, is_banbe=True)
        ).select_related(
            'nguoidung1', 'nguoidung2'
        ).values(
            'nguoidung1__id',
            'nguoidung1__avatar',
            'nguoidung1__user__username',
            'nguoidung1__user__first_name',
            'nguoidung1__user__last_name',
            'nguoidung2__id',
            'nguoidung2__avatar',
            'nguoidung2__user__username',
            'nguoidung2__user__first_name',
            'nguoidung2__user__last_name'
        )
        friend_list = []
        for friend in friends:
            if friend['nguoidung1__id'] == int(user_id):
                friend_data = {
                    'id': friend['nguoidung2__id'],
                    'avatar': friend['nguoidung2__avatar'],
                    'username': friend['nguoidung2__user__username'],
                    'first_name': friend['nguoidung2__user__first_name'],
                    'last_name': friend['nguoidung2__user__last_name']
                }
            else:
                friend_data = {
                    'id': friend['nguoidung1__id'],
                    'avatar': friend['nguoidung1__avatar'],
                    'username': friend['nguoidung1__user__username'],
                    'first_name': friend['nguoidung1__user__first_name'],
                    'last_name': friend['nguoidung1__user__last_name']
                }
            friend_list.append(friend_data)
        return JsonResponse({'friends': friend_list})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def logout(request):
    auth_logout(request)
    return redirect('login')
