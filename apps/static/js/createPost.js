
// xử lý load ảnh
document.getElementById('selectImage').addEventListener('click', function(e) {
    // Ngăn chặn hành vi mặc định của thẻ <a>
    e.preventDefault();
    // Kích hoạt input type=file khi click vào thẻ <a>
    document.getElementById('imageInput').click();
});

// Lắng nghe sự kiện thay đổi của input type=file
document.getElementById('imageInput').addEventListener('change', function() {
    // Lấy file đã chọn
    const selectedFile = this.files[0];
    if (selectedFile) {
        // Tạo đường dẫn đến file đã chọn
        const objectURL = URL.createObjectURL(selectedFile);
        // Hiển thị ảnh đã chọn lên thẻ <img>
        document.querySelector('.image-visibility').style.display = 'block';
        document.getElementById('selectedImage').src = objectURL;
        // Ẩn class select-icon
        document.querySelector('.select-icon').style.display = 'none';
    }
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
