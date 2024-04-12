
var selectedMembers = {};
var tennhom = document.getElementById("tennhom").value;

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

//xoa doan chat

