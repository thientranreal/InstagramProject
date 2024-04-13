///////////--------Phần thông báo tin nhắn mới---------////////////////////
function showPopup(sender, message) {
    var popup = document.getElementById("popup");
    var senderElement = document.getElementById("sender");
    var messageElement = document.getElementById("message");

    senderElement.textContent = sender;
    messageElement.textContent = message;

    popup.classList.add("show");
    setTimeout(function () {
        popup.classList.remove("show");
    }, 5000);
}

function closePopup() {
    var popup = document.getElementById("popup");
    popup.classList.remove("show");
}

///////////--------Hết phần thông báo tin nhắn mới---------////////////////////


///////////--------Phần tạo nhóm mới---------////////////////////
var selectedMembers = {};
function toggleMember(member) {
    if (selectedMembers[member]) {
        // Member already selected, remove from list
        delete selectedMembers[member];
    } else {
        // Add member to list
        selectedMembers[member] = true;
    }
    updateSelectedMembersList();
    document.getElementById("danhsach").value = Object.keys(selectedMembers);
}

function updateSelectedMembersList() {
    var selectedMembersList = document.getElementById("selectedMembers");
    selectedMembersList.innerHTML = "";
    for (var member in selectedMembers) {
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(member));
        li.setAttribute("onclick", "toggleMember('" + member + "')");
        selectedMembersList.appendChild(li);
    }
}

function openForm() {
    document.getElementById("myForm").style.display = "block";
}

function closeForm() {
    document.getElementById("myForm").style.display = "none";
}

document.getElementById("openFormBtn").addEventListener("click", openForm);

///////////--------Hết phần tạo nhóm mới---------////////////////////

///////////-------- phần xử lý xoá liên lạc---------////////////////////

function confirmDelete() {
    let ten = document.getElementById("receiverName").value;
    if (confirm("Bạn có muốn xoá liên lạc với " + ten + " không?")) {
        id_senter = id_user
        id_receiver = document.getElementById("id_recceiver").value;


        // const id_receiver = JSON.parse(
        //     document.getElementById("id_receiver").value
        // );

        // Thêm comment vào database
        fetch('/delete-contact/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Thêm CSRF token để Django chấp nhận yêu cầu
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                message: message,
                id_user: id_user,
                id_receiver: id_receiver,
            })
        })
        alert("Xoá thành công")
    } else {
        // Nếu người dùng không chấp nhận
    }
}

///////////-------- hết phần xử lý xoá liên lạc---------////////////////////






// để lấy thuộc tính id -->

