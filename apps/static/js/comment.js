import { csrftoken } from "./csrfToken.js";

let username = document.getElementById("username").innerText;
let notificationsBody = document.getElementById("notificationsBody");

// Websocket comment
let urlComment = `ws://${window.location.host}/ws/commment/`;
const commentSocket = new WebSocket(urlComment);

commentSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    if (data.type === "comment") {
        let postElement = document.querySelector('.post[data-id="' + data.post_id + '"]');
        let postOwner = postElement.querySelector('.username > a').innerText;
        let hienblElement = postElement.querySelector('.hienbl');
        let no_comment = document.querySelector('.no-comments');

        // Hiển thị 2 comment mới nhất
        if (no_comment.innerText === "View all comments"){
            let allDivs = Array.from(hienblElement.querySelectorAll('div')).slice(0,2);
            hienblElement.innerHTML = "";
            for (let div of allDivs) {
                hienblElement.innerHTML += div.outerHTML;
            }
        }
        // Thêm bình luận với vào bài đăng
        hienblElement.insertAdjacentHTML('afterbegin', `<div>
                                                            <img 
                                                                src="${data.avatar}" 
                                                                class="icons user-account rounded-circle" 
                                                                alt="User Profile" 
                                                                style="width: 27px; height: 27px;" />
                                                            <p>
                                                                <b>${data.username}</b>
                                                                <br />
                                                                ${data.comment}
                                                                <br />
                                                                <i>${data.timestamp}</i>
                                                            </p>
                                                        </div>`);

        // Nếu người gửi comment không phải là chủ bài đăng thì thêm thông báo cho chủ bài đăng
        if (username === postOwner && data.username !== username) {
            // Nội dung
            let noidung = `<p>${data.username} just commented your post</p>`;
            let notificationCount = document.getElementById("notification_count");

            // Thêm thông báo có người comment bài viết
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
                // Nếu thêm thành công thì sẽ hiện thông báo cho người dùng nếu là chủ bài đăng biết
                if (data.status === 'ok') {
                    // Tăng số lượng thông báo hiện có
                    if (!notificationCount) {
                        document.getElementById("notification_li").insertAdjacentHTML('afterbegin', '<span id="notification_count">1</span>');
                    }
                    else {
                        notificationCount.innerHTML = parseInt(notificationCount.innerHTML) + 1;
                    }
                    // Thêm thông báo mới vào đầu
                    notificationsBody.insertAdjacentHTML('afterbegin', noidung);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    }
};

document.querySelectorAll(".comment-box").forEach(function(element) {
    element.addEventListener("input", function(e) {
      let button = e.target.nextElementSibling;
      if (e.target.value !== "") {
        button.classList.add("active");
      } else {
        button.classList.remove("active");
      }
    });
});

// Thêm sự kiện click vào post sẽ thêm comment vào bài đăng
document.querySelectorAll(".comment-btn").forEach(function(element) {
    element.addEventListener("click", function(e) {
        if (e.target.classList.contains("active")) {
            let postElement = e.target.closest(".post");
            let postID = postElement.getAttribute("data-id");
            let comment = e.target.previousElementSibling;
            let avatar = document.getElementById("avatar").src;

            // Thêm comment vào database
            fetch('/api/comment_post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Thêm CSRF token để Django chấp nhận yêu cầu
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    post_id: postID,
                    comment: comment.value,
                })
            })
            .then(response => response.json())
            .then(data => {
                // Thêm bình luận vào database thì sẽ gửi sang websocket
                if (data.status === 'ok') {
                    // Gửi comment tới websocket
                    commentSocket.send(JSON.stringify({
                        post_id: postID,
                        comment: comment.value,
                        username: username,
                        avatar: avatar,
                        timestamp: data.timestamp
                    }));
                    comment.value = '';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
});

// Lấy ra tất cả các input có class là "comment-box"
document.querySelectorAll('.comment-box').forEach(function(inputElement) {
    // Thêm sự kiện keydown cho mỗi input
    inputElement.addEventListener('keydown', function(event) {
        // console.log(event.key);
        // Kiểm tra xem phím được nhấn có phải là phím Enter không
        if (event.key === 'Enter') {

            // Lấy ra phần tử button.comment-btn gần nhất
            let commentButton = inputElement.closest('.post').querySelector('.comment-btn');
            // Gọi sự kiện click trên button.comment-btn
            commentButton.click();
        }
    });
});


// Lắng nghe sự kiện click trên phần tử có class là 'no-comments'
document.querySelectorAll(".no-comments").forEach(function (commentElement) {
    commentElement.addEventListener("click", function () {
        // Lấy ID của bài post từ thuộc tính 'data-id' của phần tử cha
        let postId = commentElement.closest(".post").dataset.id;
        let postElement = document.querySelector('.post[data-id="' + postId + '"]');
        let hienblElement = postElement.querySelector('.hienbl');

        if (commentElement.innerText === "View all comments") {
            commentElement.innerText = "Hide comments";

            // Hiển thị comment
            fetch(`/api/comment_post?postId=${postId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                let binhluans = data.binhluan;
                hienblElement.innerHTML = '';
                for (let i = binhluans.length - 1; i >= 0; i--) {
                    const binhluan = binhluans[i];
                    if (binhluan.avatar === null) {
                        binhluan.avatar = defaultAvatarUrl;
                    }

                    hienblElement.innerHTML += `<div>
                                                    <img 
                                                        src="${binhluan.avatar}" 
                                                        class="icons user-account rounded-circle" 
                                                        alt="User Profile" 
                                                        style="width: 27px; height: 27px;" />
                                                        <p>
                                                            <b>${binhluan.username}</b>
                                                            <br />
                                                            ${binhluan.noidungbl}
                                                            <br />
                                                            <i>${binhluan.timestamp}</i>
                                                        </p>
                                                </div>`;
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        else {
            commentElement.innerText = "View all comments";

            let allDivs = Array.from(hienblElement.querySelectorAll('div')).slice(0,3);

            hienblElement.innerHTML = "";
            for (let div of allDivs) {
                hienblElement.innerHTML += div.outerHTML;
            }
        }
    });
});
