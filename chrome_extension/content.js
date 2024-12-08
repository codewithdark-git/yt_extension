// Content script for the Chrome extension
console.log('YouTube Extension Content Script Loaded');

// Function to extract video ID from YouTube URL
function getYouTubeVideoId() {
    const url = window.location.href;
    console.log('Current URL:', url);
    
    // Try to get video ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const videoId = urlParams.get('v');
    console.log('Extracted Video ID:', videoId);
    
    return videoId;
}

// Function to send video ID to background script
function sendVideoId() {
    const videoId = getYouTubeVideoId();
    if (videoId) {
        console.log('Sending video ID to background:', videoId);
        chrome.runtime.sendMessage({ type: 'VIDEO_ID', videoId: videoId }, response => {
            console.log('Background response:', response);
        });
    }
}

// Initial send
sendVideoId();

// Watch for URL changes
let lastUrl = location.href;
const observer = new MutationObserver(() => {
    const currentUrl = location.href;
    if (currentUrl !== lastUrl) {
        console.log('URL changed from', lastUrl, 'to', currentUrl);
        lastUrl = currentUrl;
        sendVideoId();
    }
});

// Start observing
observer.observe(document, { subtree: true, childList: true });

// Also check periodically (as backup)
setInterval(sendVideoId, 5000);

// You can add more content script functionalities here
