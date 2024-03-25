from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
# Hàm tạo đường dẫn hình ảnh cho người dùng
def user_directory_path(instance, filename):
    # file sẽ được lưu vào MEDIA_ROOT / hinh_anh/user_<id>/<filename>
    return 'images/user_{0}/{1}'.format(instance.user.id, filename)


# Trong User đã có trường email, first name, last name, password
# Nên NguoiDung k cần những trường trên
class NguoiDung(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    ngaysinh = models.DateField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=user_directory_path)
    sobanbe = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_online = models.BooleanField(default=False, blank=True, null=True)
    gioitinh=models.CharField(max_length=15, blank=True, null=True)
    mota=models.TextField(blank=True, null=True)



class BanBe(models.Model):
    nguoidung1 = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, related_name='ban_be_1')
    nguoidung2 = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, related_name='ban_be_2')

class TinNhan(models.Model):
    senter = models.ForeignKey('NguoiDung', on_delete=models.CASCADE,related_name='nguoi_dung_1')
    receiver = models.ForeignKey('NguoiDung', on_delete =models.CASCADE,related_name='nguoi_dung_2')
    noidung = models.TextField(blank=True, null=True)
    thoigian = models.DateTimeField(blank=True, null=True)

class LienLac(models.Model):
    goc = models.ForeignKey('NguoiDung', on_delete=models.CASCADE,related_name='goc')
    dich = models.ForeignKey('NguoiDung', on_delete =models.CASCADE,related_name='dich')
    lastmess = models.TextField(blank=True, null=True)
    thoigiancuoi = models.DateTimeField(blank=True, null=True)

class BaiDang(models.Model): 
    nguoidung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE)
    noidung = models.TextField(blank=True, null=True)
    thoigiandang = models.DateTimeField(blank=True, null=True)
    tongluotthich = models.IntegerField(blank=True, null=True)
    tongluotbinhluan = models.IntegerField(blank=True, null=True)
    hinhanh = models.ImageField(blank=True, null=True, upload_to='images/')

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

