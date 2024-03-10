import { csrftoken } from "./csrfToken.js";

// Hàm kiểm tra email
function isEmail(value) {
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/;
    return emailRegex.test(value);
}

// Hàm kiểm tra số điện thoại
function isPhoneNumber(phoneNumber) {
    const phoneRegex = /^(03|05|07|08|09|01[2|6|8|9])+([0-9]{8})\b/;
    return phoneRegex.test(phoneNumber);
}

let showError = document.querySelector('.error');
let inputs = document.querySelectorAll('form > input');
let signupBtn = document.getElementById("sign-up-btn");

let phone_email = inputs[0];
let firstname = inputs[1];
let lastname = inputs[2];
let username = inputs[3];
let password = inputs[4];

phone_email.focus();

// Gắn sự kiện enter cho input
inputs.forEach(function(input) {
    input.addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            signupBtn.click();
        }
    });
});



signupBtn.addEventListener('click', function(e) {
    // Kiểm tra dữ liệu được nhập
    // Nếu là chuỗi số mà không đúng định dạng số điện thoại
    if (!isNaN(phone_email.value) && !isPhoneNumber(phone_email.value)) {
        showError.innerHTML = "Looks like your phone number may be incorrect. Please try entering your full number, including the country code.";
        phone_email.focus();
        return;
    }
    // Nếu mà không phải chuỗi số và không đúng định dạng email
    if (isNaN(phone_email.value) && !isEmail(phone_email.value)) {
        showError.innerHTML = "Enter a valid email address.";
        phone_email.focus();
        return;
    }
    // Nếu không nhập first name
    if (firstname.value.trim() === "") {
        showError.innerHTML = "Enter first name.";
        firstname.focus();
        return;
    }
    // Nếu không nhập last name
    if (lastname.value.trim() === "") {
        showError.innerHTML = "Enter last name.";
        lastname.focus();
        return;
    }
    // Nếu không nhập user name
    if (username.value.trim() === "") {
        showError.innerHTML = "Enter user name.";
        username.focus();
        return;
    }
    // Nếu không nhập password
    if (password.value === "") {
        showError.innerHTML = "Enter password.";
        password.focus();
        return;
    }

    fetch('/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Thêm CSRF token để Django chấp nhận yêu cầu
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            phone_email: phone_email.value,
            firstname: firstname.value,
            lastname: lastname.value,
            username: username.value,
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
  