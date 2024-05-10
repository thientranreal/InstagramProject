let username = document.getElementById("username").innerText;

// Websocket add friend
let urlAddFriend = `ws://${window.location.host}/ws/addfriend/`;
const addFriendSocket = new WebSocket(urlAddFriend);

addFriendSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    
    if (data.receive_user === username) {
        location.reload();
    }
};

document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.querySelector('.search');
    if (searchInput) { 
        searchInput.addEventListener('input', function() {
            var searchData = this.value; 
            search(searchData);
        });
    }
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
                                <h6 class="m-0"><a href="profile_friend/${user.id}" class="profile-link">${user.user__username}</a></h6>
                                <p class="text-muted name">${user.user__last_name} ${user.user__first_name}</p>
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
                                <h6 class="m-0"><a href="profile_friend/${user.nguoidung2__id}" class="profile-link">${user.nguoidung2__user__username}</a></h6>
                                <p class="text-muted name">${user.nguoidung2__user__last_name} ${user.nguoidung2__user__first_name}</p>
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
                                <h6 class="m-0"><a href="profile_friend/${user.nguoidung1__id}" class="profile-link">${user.nguoidung1__user__username}</a></h6>
                                <p class="text-muted name">${user.nguoidung1__user__last_name} ${user.nguoidung1__user__first_name}</p>
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
                                <h6 class="m-0"><a href="profile_friend/${user.id}" class="profile-link">${user.user__username}</a></h6>
                                <p class="text-muted name">${user.user__last_name} ${user.user__first_name}</p>
                            </div>
                            <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                            <button data-product="${user.user__username}" data-action="remove" class="btn btn-white border-dark remove-btn updatefriend">Unfriend</button>
                            </div>
                        </div>
                    </div>`;
            }
        }
        attachEventListeners();
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
    
}

var btnUpdate = document.getElementsByClassName('updatefriend');
for (let index = 0; index < btnUpdate.length; index++) {
    btnUpdate[index].addEventListener('click', function () {
        var userId = this.dataset.product;
        var action = this.dataset.action;
        updateUserOrder(this,userId, action);
    });
}

function updateUserOrder(element, userId, action) {
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

            let noidung;
            if (action === "add") {
                noidung = `<p>${username} has requested to follow you</p>`;
            }
            else if (action === "accept") {
                noidung = `<p>${username} has accepted you</p>`;
            }
            else {
                // Gửi qua websocket
                addFriendSocket.send(JSON.stringify({
                    receive_user: userId,
                    noidung: "unfriend",
                }));
            }

            if (noidung) {
                // Thêm thông báo có người kết bạn
                fetch('/add_notification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // Thêm CSRF token để Django chấp nhận yêu cầu
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        nguoidung: userId,
                        noidung: noidung,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // Nếu thêm thông báo thành công vào db thì sẽ gửi web socket
                    if (data.status === 'ok') {
                        // Gửi qua websocket
                        addFriendSocket.send(JSON.stringify({
                            receive_user: userId,
                            noidung: noidung,
                        }));
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }


            if (data.message === 'Friendship added successfully') {
                var successMessage = document.createElement('p');
                successMessage.textContent = 'Đã gửi lời mời';
                element.parentNode.insertBefore(successMessage, element);
                element.style.display = 'none';
                // element.parentNode.removeChild(element);
                
            }else if(data.message === 'Friendship removed successfully'){
                var successMessage = document.createElement('p');
                successMessage.textContent = 'Đã xóa bạn bè';
                element.parentNode.insertBefore(successMessage, element);
                element.style.display = 'none';

            }else if(data.message === 'Friendship cancel successfully'){
                var successMessage = document.createElement('p');
                successMessage.textContent = 'Đã hủy lời mời';
                element.parentNode.insertBefore(successMessage, element);
                element.style.display = 'none';
                
            }else if(data.message === 'Friendship accepted successfully'){
                var successMessage = document.createElement('p');
                successMessage.textContent = 'Đã trở thành bạn bè';
                element.parentNode.insertBefore(successMessage, element);
                element.style.display = 'none';
                var acceptBtn = element.parentNode.querySelector('.refuse-btn');
                if (acceptBtn) {
                    acceptBtn.style.display = 'none';
                }

            }else if(data.message === 'Friendship refuse successfully'){
                var successMessage = document.createElement('p');
                successMessage.textContent = 'Đã hủy lời mời kết bạn';
                element.parentNode.insertBefore(successMessage, element);
                element.style.display = 'none';
                var acceptBtn = element.parentNode.querySelector('.accept-btn');
                if (acceptBtn) {
                    acceptBtn.style.display = 'none';
                }
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function attachEventListeners() {
    var btnUpdate = document.querySelectorAll('.updatefriend');
    console.log(btnUpdate)
    btnUpdate.forEach(function(button) {
        button.addEventListener('click', function () {
            var userId = this.dataset.product;
            var action = this.dataset.action;
            updateUserOrder(this, userId, action);
        });
    });
}

document.querySelectorAll('h6.suggest').forEach(function(h6) {
    h6.addEventListener('click', function() {
      var nearbyUser = document.querySelector('.suggestDiv');
      if (nearbyUser.style.display === 'none') {
        nearbyUser.style.display = 'block';
      } else {
        nearbyUser.style.display = 'none';
      }
    });
  });

document.querySelectorAll('h6.invitation').forEach(function(h6) {
    h6.addEventListener('click', function() {
        var nearbyUser = document.querySelector('.invitationDiv');
        if (nearbyUser.style.display === 'none') {
        nearbyUser.style.display = 'block';
        } else {
        nearbyUser.style.display = 'none';
        }
    });
});

document.querySelectorAll('h6.request').forEach(function(h6) {
    h6.addEventListener('click', function() {
        var nearbyUser = document.querySelector('.requestDiv');
        if (nearbyUser.style.display === 'none') {
        nearbyUser.style.display = 'block';
        } else {
        nearbyUser.style.display = 'none';
        }
    });
});

document.querySelectorAll('h6.friend').forEach(function(h6) {
    h6.addEventListener('click', function() {
        var nearbyUser = document.querySelector('.friendDiv');
        if (nearbyUser.style.display === 'none') {
        nearbyUser.style.display = 'block';
        } else {
        nearbyUser.style.display = 'none';
        }
    });
});