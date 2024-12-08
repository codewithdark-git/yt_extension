// Background script for the Chrome extension
console.log('Background Script Loaded');

// Store current video ID
let currentVideoId = null;

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Received message:', message);
    
    if (message.type === 'VIDEO_ID') {
        currentVideoId = message.videoId;
        console.log('Updated current video ID:', currentVideoId);
        // Notify all open popups about the new video ID
        chrome.runtime.sendMessage({ type: 'VIDEO_ID_UPDATED', videoId: currentVideoId });
        sendResponse({ success: true });
    }
    else if (message.type === 'GET_VIDEO_ID') {
        console.log('Sending video ID to popup:', currentVideoId);
        sendResponse({ videoId: currentVideoId });
    }
    return true; // Keep the message channel open for async response
});

// When extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed/updated');
    currentVideoId = null;
});

// You can add more background functionalities here
