// const posts = document.querySelectorAll('.gallery-item');

// posts.forEach(post => {
// 	post.addEventListener('click', () => {
// 		//Get original image URL
// 		const imgUrl = post.firstElementChild.src.split("?")[0];
// 		//Open image in new tab
// 		window.open(imgUrl, '_blank');
// 	});
// });

// hiển thị nút xóa sửa
var hideTimer;

function showDropdown() {
    var dropdownMenus = document.querySelectorAll('.dropdown-menu');
    dropdownMenus.forEach(function(dropdownMenu) {
        dropdownMenu.classList.add('show');
    });
}

function hideDropdown() {
    hideTimer = setTimeout(function() {
        var dropdownMenus = document.querySelectorAll('.dropdown-menu');
        dropdownMenus.forEach(function(dropdownMenu) {
            dropdownMenu.classList.remove('show');
        });
    }, 100); // Ẩn menu sau 1 giây
}

function cancelHideTimer() {
    clearTimeout(hideTimer);
}

