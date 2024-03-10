// app.js
const startButton = document.getElementById('startButton');
const hangupButton = document.getElementById('hangupButton');
let localStream;
let peerConnection;

startButton.addEventListener('click', startCall);
hangupButton.addEventListener('click', hangupCall);

async function startCall() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        document.getElementById('localVideo').srcObject = localStream;

        // Create peer connection
        peerConnection = new RTCPeerConnection();

        // Add local stream to peer connection
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

        // Handle remote tracks
        peerConnection.ontrack = function(event) {
            document.getElementById('remoteVideo').srcObject = event.streams[0];
        };

        // Send offer to peer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        // Send offer to backend
        const jsonOffer = JSON.stringify(offer);
        const csrfToken = getCSRFToken(); // You need to implement this function to get the CSRF token
        const response = await fetch('/send_offer/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: jsonOffer,
        });
    } catch (error) {
        console.error('Error starting call:', error);
    }
}

async function hangupCall() {
    localStream.getTracks().forEach(track => track.stop());
    peerConnection.close();
}

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}
