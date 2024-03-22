
// xử lý load ảnh
document.getElementById('changeImg').addEventListener('click', function(e) {
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
        document.getElementById('selectedAvt').src = objectURL;
        // Ẩn class select-icon\
    }
});
// end
