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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
