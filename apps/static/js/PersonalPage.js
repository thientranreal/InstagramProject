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
document.addEventListener('DOMContentLoaded', function() {
    var loadfriend = document.querySelectorAll('.loadFriend');
    loadfriend.forEach(function(iconLike) {
        iconLike.addEventListener('click', function() {
            var id = this.dataset.product; 
            console.log("aaaaa");
            loadFriend(id);
        });
    });
});

function loadFriend(id) {
    var csrftoken = getCookie('csrftoken'); // Assume you have a function to get csrf token
    var url = '/loadfriend/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'id': id
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        var load = document.querySelector('.hienfriend');
        load.innerHTML = '';
        if (data.friends.length > 0) {
            var friend = data.friends;
            load.innerHTML += `<div style="position: absolute; top: 0; right: 0; padding: 5px;">
            <i class="fas fa-times" onclick="hidehienfriend(this)"></i>
            </div>
            <h3 class=" text-center">Danh sách bạn bè</h3>
            <hr class="bg-dark">`;
            for (let i = 0; i < friend.length; i++) {
                const user = friend[i];
                load.innerHTML += `
                <div class="nearby-user">
                    <div class="row mb-3" style="margin: 0">
                        <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                            <img src="/media/${user.avatar}" alt="user" class="profile-photo-lg mx-auto d-block" style="height: 40px; width: 40px;">
                        </div>
                        <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                            <h6 class="m-0"><a href="profile_friend/${user.id}" class="profile-link">${user.username}</a></h6>
                            <p class="text-muted name">${user.last_name} ${user.first_name}</p>
                        </div>
                        <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                            <button data-product="${user.username}" data-action="remove" class="btn btn-white border-dark remove-btn updatefriend">Unfriend</button>
                        </div>
                    </div>
                </div>`;
            }
        }
        attachEventListeners()
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
}

function hidehienfriend(element) {
    var hienUserLike = element.closest('.hienfriend');
    hienUserLike.style.display = "none";
}

function attachEventListeners() {
    var btnUpdate = document.querySelectorAll('.updatefriend');
    btnUpdate.forEach(function(button) {
        button.addEventListener('click', function () {
            var userId = this.dataset.product;
            var action = this.dataset.action;
            updateUserOrder(this, userId, action);
        });
    });
}

