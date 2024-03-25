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
    gioitinh=models.CharField(max_length=15, blank=True, null=True)
    mota=models.TextField(blank=True, null=True)

    # is_online = models.BooleanField(default=False)

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



# Thêm dữ liệu cho lớp NguoiDung
# for i in range(10):
#     nguoidung = NguoiDung.objects.create(
#         ngaysinh=datetime.now(),
#         sobanbe=10,
#         phone='0123456789'
#     )
#     # Lưu ý: Trường user cần được gán sau khi tạo user

# # Thêm dữ liệu cho lớp BanBe
# nguoidungs = NguoiDung.objects.all()
# for i in range(10):
#     BanBe.objects.create(
#         nguoidung1=nguoidungs[i],
#         nguoidung2=nguoidungs[i+1] if i < 9 else nguoidungs[0]
#     )

# # Thêm dữ liệu cho lớp TinNhan
# for i in range(10):
#     TinNhan.objects.create(
#         senter=nguoidungs[i],
#         receiver=nguoidungs[i+1] if i < 9 else nguoidungs[0],
#         noidung=f'Tin nhan thu {i+1}',
#         thoigian=datetime.now()
#     )

# # Thêm dữ liệu cho lớp LienLac
# for i in range(10):
#     LienLac.objects.create(
#         goc=nguoidungs[i],
#         dich=nguoidungs[i+1] if i < 9 else nguoidungs[0],
#         lastmess=f'Tin nhan cuoi cung giua {nguoidungs[i]} va {nguoidungs[i+1] if i < 9 else nguoidungs[0]}',
#         thoigiancuoi=datetime.now()
#     )

# # Thêm dữ liệu cho lớp BaiDang
# for i in range(10):
#     BaiDang.objects.create(
#         nguoidung=nguoidungs[i],
#         noidung=f'Noi dung bai dang thu {i+1}',
#         thoigiandang=datetime.now(),
#         tongluotthich=0,
#         hinhanh='duongdananh.jpg'
#     )

# # Thêm dữ liệu cho lớp ThongBao
# for i in range(10):
#     ThongBao.objects.create(
#         nguoidung=nguoidungs[i],
#         noidung=f'Noi dung thong bao thu {i+1}',
#         is_read=False,
#         timestamp=datetime.now()
#     )

# # Thêm dữ liệu cho lớp BinhLuan
# baidangs = BaiDang.objects.all()
# for i in range(10):
#     BinhLuan.objects.create(
#         baidang=baidangs[i],
#         nguoidung=nguoidungs[i],
#         noidungbl=f'Noi dung binh luan thu {i+1}',
#         timestamp=datetime.now()
#     )