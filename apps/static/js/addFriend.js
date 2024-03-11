var btnUpdate = document.getElementsByClassName('updatefriend');
for (let index = 0; index < btnUpdate.length; index++) {
    btnUpdate[index].addEventListener('click', function () {
        var userId = this.dataset.product;
        var action = this.dataset.action;
        updateUserOrder(userId, action);
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
            location.reload(); 
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
