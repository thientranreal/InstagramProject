import { csrftoken } from "./csrfToken.js";

// Kiểm tra người dùng có đang đăng nhập không
fetch('/api/check_login_status', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    },
})
.then(response => response.json())
.then(data => {
    if (data.status === 'login') {
        window.location.href = '/home';
    }
    else if (data.status === 'not login') {
        LoginPage();
    }
})
.catch((error) => {
    console.error('Error:', error);
});

function LoginPage() {
    let identifier = document.querySelector('input[name="identifier"]');
    let password = document.querySelector('input[name="password"]');
    let loginBtn = document.getElementById('login-btn');
    let showError = document.querySelector('.error');

    identifier.focus();

    identifier.addEventListener("input", function(e) {
        if (e.target.value !== "" && password.value != "") {
            loginBtn.removeAttribute('disabled');
        } else {
            loginBtn.setAttribute('disabled','');
        }
    });

    password.addEventListener("input", function(e) {
        if (e.target.value !== "" && identifier.value != "") {
            loginBtn.removeAttribute('disabled');
        } else {
            loginBtn.setAttribute('disabled','');
        }
    });

    // Sự kiện nhấn enter để đăng nhập cho username
    identifier.addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            loginBtn.click();
        }
    });

    // Sự kiện nhấn enter để đăng nhập cho password
    password.addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            loginBtn.click();
        }
    });
    

    loginBtn.addEventListener("click", function(e) {

        fetch('/login', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            // Thêm CSRF token để Django chấp nhận yêu cầu
            'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                identifier: identifier.value,
                password: password.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                showError.innerHTML = data.message;
            }
            else if (data.status === 'ok') {
                showError.innerHTML = "";
                window.location.href = '/home';
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
}
