
// xử lý load ảnh
document.getElementById('selectImage').addEventListener('click', function(e) {
    // Ngăn chặn hành vi mặc định của thẻ <a>
    e.preventDefault();
    // Kích hoạt input type=file khi click vào thẻ <a>
    document.getElementById('imageInput').click();
});

// Lắng nghe sự kiện thay đổi của input type=file
document.addEventListener('DOMContentLoaded', function () {
    // Lấy file đã chọn
    const imageInput  = document.getElementById('imageInput');
    const croppedImage =document.getElementById('selectedImage');
    let cropper;
    imageInput.addEventListener('change', function () {
        const file = this.files[0];
        const reader = new FileReader();

        reader.onload = function (event) {
            const img = new Image();
            img.src = event.target.result;

            img.onload = function () {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                // Kích thước của phần cắt
                let size = Math.min(img.width, img.height);
                let x = (img.width - size) / 2;
                let y = (img.height - size) / 2;

                // Tạo canvas vuông với kích thước cố định
                canvas.width = 300; // Đổi kích thước tùy ý
                canvas.height = 300; // Đổi kích thước tùy ý

                // Vẽ phần cắt của ảnh lên canvas
                ctx.drawImage(img, x, y, size, size, 0, 0, canvas.width, canvas.height);

                // Hiển thị ảnh đã cắt lên thẻ img
                croppedImage.src = canvas.toDataURL();
            };
        };

        reader.readAsDataURL(file);
    });
});
// end

// xử lý add-icon
document.addEventListener('DOMContentLoaded', function() {
    // Chọn tất cả các phần tử img có class là add-icon
    var addIcons = document.querySelectorAll('.add-icon');
    
    // Lặp qua từng phần tử để thêm sự kiện click
    addIcons.forEach(function(icon) {
        icon.addEventListener('click', function() {
            // Chuyển hướng đến trang createPost.html
            window.location.href = 'createPost.html';
        });
    });
});
