from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
# Hàm tạo đường dẫn hình ảnh cho người dùng
def user_directory_path(instance, filename):
    # file sẽ được lưu vào MEDIA_ROOT / hinh_anh/user_<id>/<filename>
    return f'images/user_{instance.user.username}/avatars/{filename}'

# Hàm tạo đường dẫn hình ảnh cho bài đăng
def user_directory_post_path(instance, filename):
    # file sẽ được lưu vào MEDIA_ROOT / hinh_anh/user_<id>/<filename>
    return f'images/user_{instance.nguoidung.user.username}/posts/{filename}'

class NguoiDung(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    ngaysinh = models.DateField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=user_directory_path, default='images/download.png')
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_online = models.BooleanField(default=False, blank=True, null=True)
    gioitinh=models.CharField(max_length=15, blank=True, null=True)
    mota=models.TextField(blank=True, null=True)
    
    def tong_luot_banbe(self):
        return BanBe.objects.filter(models.Q(nguoidung1=self, is_banbe=True) | models.Q(nguoidung2=self, is_banbe=True)).count()

class BanBe(models.Model):
    nguoidung1 = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, related_name='ban_be_1')
    nguoidung2 = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, related_name='ban_be_2')
    is_banbe = models.BooleanField(default=False, blank=True, null=True)
    thoigian = models.DateTimeField(blank=True, null=True)
    lastmess = models.TextField(blank=True, null=True)
    thoigiancuoi = models.DateTimeField(blank=True, null=True)

class TinNhan(models.Model):
    senter = models.ForeignKey('NguoiDung', on_delete=models.CASCADE,related_name='nguoi_dung_1')
    receiver = models.ForeignKey('NguoiDung', on_delete =models.CASCADE,related_name='nguoi_dung_2')
    noidung = models.TextField(blank=True, null=True)
    thoigian = models.DateTimeField(blank=True, null=True)

# class LienLac(models.Model):
#     goc = models.ForeignKey('NguoiDung', on_delete=models.CASCADE,related_name='goc')
#     dich = models.ForeignKey('NguoiDung', on_delete =models.CASCADE,related_name='dich')
#     is_banbe = models.BooleanField(default=False, blank=True, null=True)
class Nhom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    nguoidung = models.ManyToManyField('NguoiDung', blank=True)
    admin = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, blank=True, null=True, related_name='admin')
    lasstmess = models.TextField(blank=True, null=True)
    thoigiancuoi = models.DateTimeField(blank=True, null=True)
    
class TinNhanNhom(models.Model):
    nhom = models.ForeignKey('Nhom', on_delete=models.CASCADE ,related_name='nhom')
    noidung = models.TextField(blank=True, null=True)
    sender = models.ForeignKey('NguoiDung', on_delete=models.CASCADE,related_name='nguoi_dung')
    thoigian = models.DateTimeField(blank=True, null=True)
    
class BaiDang(models.Model): 
    nguoidung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE)
    noidung = models.TextField(blank=True, null=True)
    thoigiandang = models.DateTimeField(blank=True, null=True)
    hinhanh = models.ImageField(blank=True, null=True, upload_to=user_directory_post_path)

    def tong_luot_binh_luan(self):
        return self.binhluan_set.count() 
    
    def tong_luot_thich(self):
        return self.likebaidang_set.count() 

class ThongBao(models.Model):
    nguoidung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE)
    noidung = models.TextField(blank=True, null=True)  #Luu thẳng cái mã HTML vô rồi chỉ cần in toàn bộ ra
    is_read = models.BooleanField(default=False) 
    timestamp = models.DateTimeField(auto_now_add=True)

class BinhLuan(models.Model):
    baidang = models.ForeignKey('BaiDang', on_delete=models.CASCADE)
    nguoidung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE)
    noidungbl = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class LikeBaiDang(models.Model):
    baidang = models.ForeignKey('BaiDang', on_delete=models.CASCADE)
    nguoidung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE)
    thoigian = models.DateTimeField(auto_now_add=True)
