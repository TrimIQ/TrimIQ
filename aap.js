// app.js
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('trimIQ_token');
    if (!token && !window.location.pathname.endsWith('/login.html') && !window.location.pathname.endsWith('/register.html')) {
        window.location.href = '/login.html';
    }

    // Editor functionality
    if (window.location.pathname.endsWith('/editor.html')) {
        initEditor();
    }
});

function initEditor() {
    // Handle video upload
    const videoUpload = document.getElementById('video-upload');
    const videoInput = document.getElementById('video-input');
    
    videoUpload.addEventListener('click', () => videoInput.click());
    videoInput.addEventListener('change', handleVideoUpload);
    
    // Handle audio upload
    const audioUpload = document.getElementById('audio-upload');
    const audioInput = document.getElementById('audio-input');
    
    audioUpload.addEventListener('click', () => audioInput.click());
    audioInput.addEventListener('change', handleAudioUpload);
    
    // Generate button
    document.getElementById('generate-btn').addEventListener('click', generateVideo);
    
    // Payment toggle
    document.getElementById('payment-toggle').addEventListener('change', togglePaymentMode);
    
    // Logout
    document.getElementById('logout').addEventListener('click', logout);
    
    // Load user balance
    fetchUserBalance();
}

async function fetchUserBalance() {
    try {
        const response = await fetch('/api/balance', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('trimIQ_token')}`
            }
        });
        const data = await response.json();
        document.getElementById('user-balance').textContent = `Balance: ₹${data.balance.toFixed(2)}`;
        document.getElementById('total-earnings').textContent = `Earned: ₹${data.ad_revenue.toFixed(2)}`;
    } catch (error) {
        console.error('Error fetching balance:', error);
    }
}

function logout() {
    localStorage.removeItem('trimIQ_token');
    window.location.href = '/login.html';
}
