let username = document.getElementById("username").innerText;

// Websocket add friend
let urlAddFriend = `ws://${window.location.host}/ws/addfriend/`;
const addFriendSocket = new WebSocket(urlAddFriend);

addFriendSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    // Nếu là type add và đang được người khác kết bạn
    if (data.type === "add" && data.friend_username === username) {
        // Nội dung
        let noidung = `<p>${data.current_user} has requested to follow you</p>`;

        // Thêm thông báo có người kết bạn
        fetch('/add_notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Thêm CSRF token để Django chấp nhận yêu cầu
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                noidung: noidung,
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
        })
        .catch((error) => {
            console.error('Error:', error);
        });

        location.reload();
    }
    // Khi có hành động bất kì liên quan đến người được kết bạn
    else if (data.friend_username === username) {
        location.reload();
    }
};

var btnUpdate = document.getElementsByClassName('updatefriend');
for (let index = 0; index < btnUpdate.length; index++) {
    btnUpdate[index].addEventListener('click', function () {
        var userId = this.dataset.product;
        var action = this.dataset.action;
        updateUserOrder(userId, action);
    });
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.search').addEventListener('input', function() {
        var searchData = this.value; 
        search(searchData);
    });
});

function search(searchData) {
    var url = '/friend';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'searchData': searchData, 
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        var load = document.querySelector('.people-nearby');
        load.innerHTML = '';
        if (data.other_users.length > 0) {
            var otherUsersData = data.other_users;
            load.innerHTML += '<h6 class="mb-3"><a href="#" class="profile-link">Gợi ý kết bạn</a></h6>';
            for (let i = 0; i < otherUsersData.length; i++) {
                const user = otherUsersData[i];
        
                load.innerHTML += `
                    <div class="nearby-user">
                        <div class="row mb-3">
                            <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                                <img src="/media/${user.avatar}" alt="user" class="profile-photo-lg mx-auto d-block">
                            </div>
                            <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                                <h6 class="m-0"><a href="#" class="profile-link">${user.user__username}</a></h6>
                                <p class="text-muted name">${user.user__last_name} ${user.user__first_name}</p>
                                <p class="text-muted m-0">${user.sobanbe} Friend</p>
                            </div>
                            <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                                <button data-product="${user.user__username}" data-action="add" class="btn btn-primary pull-right add-btn updatefriend">Add friend</button>
                            </div>
                        </div>
                    </div>`;
            }
        }
    
        if (data.sender_friend_ids.length > 0) {
            var sender_friend_ids = data.sender_friend_ids;
            load.innerHTML += '<h6 class="mt-3 mb-3"><a href="#" class="profile-link">Lời mời đã gửi</a></h6>';
            for (let i = 0; i < sender_friend_ids.length; i++) {
                const user = sender_friend_ids[i];
                load.innerHTML += `
                    <div class="nearby-user">
                        <div class="row mb-3">
                            <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                                <img src="/media/${user.nguoidung2__avatar}" alt="user" class="profile-photo-lg mx-auto d-block">
                            </div>
                            <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                                <h6 class="m-0"><a href="#" class="profile-link">${user.nguoidung2__user__username}</a></h6>
                                <p class="text-muted name">${user.nguoidung2__user__last_name} ${user.nguoidung2__user__first_name}</p>
                                <p class="text-muted m-0">${user.nguoidung2__sobanbe} Friend</p>
                            </div>
                            <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                                <button data-product="${user.nguoidung2__user__username}" data-action="cancel" class="btn btn-white border-dark cancel-btn updatefriend">Cancel</button>
                            </div>
                        </div>
                    </div>`;
            }
        }
        if (data.receiver_friend_ids.length > 0) {
            var receiver_friend_ids = data.receiver_friend_ids;
            load.innerHTML += '<h6 class="mt-3 mb-3"><a href="#" class="profile-link">Yêu cầu kết bạn</a></h6>';
            for (let i = 0; i < receiver_friend_ids.length; i++) {
                const user = receiver_friend_ids[i];
                load.innerHTML += `
                    <div class="nearby-user">
                        <div class="row mb-3">
                            <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                                <img src="/media/${user.nguoidung1__avatar}" alt="user" class="profile-photo-lg mx-auto d-block">
                            </div>
                            <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                                <h6 class="m-0"><a href="#" class="profile-link">${user.nguoidung1__user__username}</a></h6>
                                <p class="text-muted name">${user.nguoidung1__user__last_name} ${user.nguoidung1__user__first_name}</p>
                                <p class="text-muted m-0">${user.nguoidung1__sobanbe} Friend</p>
                            </div>
                            <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                                <button data-product="${user.nguoidung1__user__username}" data-action="accept" class="btn btn-primary me-3 pull-right accept-btn updatefriend">Accept</button>
                                <button data-product="${user.nguoidung1__user__username}" data-action="refuse" class="btn btn-white border-dark refuse-btn updatefriend">Refuse</button>
                            </div>
                        </div>
                    </div>`;
            }
        }

        if (data.friends.length > 0) {
            var friends = data.friends;
            load.innerHTML += '<h6 class="mt-3 mb-3"><a href="#" class="profile-link">Bạn bè</a></h6>';
            for (let i = 0; i < friends.length; i++) {
                const user = friends[i];
                load.innerHTML += `
                    <div class="nearby-user">
                        <div class="row mb-3">
                            <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                                <img src="/media/${user.avatar}" alt="user" class="profile-photo-lg mx-auto d-block">
                            </div>
                            <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                                <h6 class="m-0"><a href="#" class="profile-link">${user.user__username}</a></h6>
                                <p class="text-muted name">${user.user__last_name} ${user.user__first_name}</p>
                                <p class="text-muted m-0">${user.sobanbe} Friend</p>
                            </div>
                            <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                            <button data-product="${user.user__username}" data-action="remove" class="btn btn-white border-dark remove-btn updatefriend">Unfriend</button>
                            </div>
                        </div>
                    </div>`;
            }
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
    
}

function updateUserOrder(userId, action) {
    var url = '/updatefriend/';
    fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'userId': userId,
                'action': action
            })
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            console.log('Data:', data);

            // Gửi qua websocket
            addFriendSocket.send(JSON.stringify({
                friendUsername: userId,
                currentUser: username,
                action: action,
            }));

            location.reload();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
