document.addEventListener('DOMContentLoaded', function() {
    var iconLikes = document.querySelectorAll('.iconLike');
    iconLikes.forEach(function(iconLike) {
        iconLike.addEventListener('click', function() {
            var idPost = this.dataset.product; 
            var action = this.dataset.action;
            updatelike(idPost, action);
        });
    });
});

function updatelike(idPost, action) {
    var csrftoken = getCookie('csrftoken'); // Assume you have a function to get csrf token
    var url = '/updatelike/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'idPost': idPost, 
            'action': action
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        location.reload(); 
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var iconLikes = document.querySelectorAll('.loadUserLike');
    iconLikes.forEach(function(iconLike) {
        iconLike.addEventListener('click', function() {
            var idPost = this.dataset.product; 
            loadUserLike(idPost);
        });
    });
});

function loadUserLike(idPost) {
    var csrftoken = getCookie('csrftoken'); // Assume you have a function to get csrf token
    var url = '/loaduserlike/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'idPost': idPost
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        var load = document.querySelector('.hienUserLike');
        load.innerHTML = '';
        if (data.likeUsers.length > 0) {
            var likeUsers = data.likeUsers;
            load.innerHTML += `<div style="position: absolute; top: 0; right: 0; padding: 5px;">
            <i class="fas fa-times" onclick="hideHienUserLike(this)"></i>
            </div>
            <h3 class=" text-center">Lượt thích</h3>
            <hr class="bg-dark">`;
            for (let i = 0; i < likeUsers.length; i++) {
                const user = likeUsers[i];
                let buttonHtml = '';
                if (user.friendStatus === false) {
                    buttonHtml = `<button data-product="${user.user__username}" data-action="add" class="btn btn-primary pull-right add-btn updatefriend">Add friend</button>`;
                } else if (user.friendStatus === true) {
                    buttonHtml = `<button data-product="${user.user__username}" data-action="remove" class="btn btn-white border-dark remove-btn updatefriend">Unfriend</button>`;
                } else if (user.friendStatus === "pending_sender") {
                    buttonHtml = `<button data-product="${user.user__username}" data-action="cancel" class="btn btn-white border-dark cancel-btn updatefriend">Cancel</button>`;
                } else if (user.friendStatus === "pending_receiver") {
                    buttonHtml = `<button data-product="${user.user__username}" data-action="accept" class="btn btn-primary me-3 pull-right accept-btn updatefriend">Accept</button>
                                  <button data-product="${user.user__username}" data-action="refuse" class="btn btn-white border-dark refuse-btn updatefriend">Refuse</button>`;
                }
                load.innerHTML += `
                <div class="nearby-user">
                    <div class="row mb-3" style="margin: 0">
                        <div class="col-md-2 col-sm-2 d-flex align-items-center justify-content-center">
                            <img src="/media/${user.avatar}" alt="user" class="profile-photo-lg mx-auto d-block" style="height: 40px; width: 40px;">
                        </div>
                        <div class="col-md-7 col-sm-7 d-flex flex-column justify-content-center">
                            <h6 class="m-0"><a href="profile_friend/${user.id}" class="profile-link">${user.user__username}</a></h6>
                            <p class="text-muted name">${user.user__last_name} ${user.user__first_name}</p>
                        </div>
                        <div class="col-md-3 col-sm-3 d-flex align-items-center justify-content-center">
                            ${buttonHtml}
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

function hideHienUserLike(element) {
    var hienUserLike = element.closest('.hienUserLike');
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

    let currentScroll = 0;
    let scrollAmount = 320;

    const sCont = document.querySelector(".stories");
    const hScroll = document.querySelector(".status-wrapper");
    const leftButton = document.querySelector("#scroll-left");
    const rightButton = document.querySelector("#scroll-right");

    let maxScroll = -sCont.offsetWidth + hScroll.offsetWidth;
    leftButton.style.opacity = "0";

    function scrollHorizontal(val) {
    currentScroll += val * scrollAmount;
    if (currentScroll >= 0) {
        currentScroll = 0;
        leftButton.style.opacity = "0";
    } else {
        leftButton.style.opacity = "1";
    }
    if (currentScroll <= maxScroll) {
        currentScroll = maxScroll;
        rightButton.style.opacity = "0";
    } else {
        rightButton.style.opacity = "1";
    }
    sCont.style.left = currentScroll + "px";
    }