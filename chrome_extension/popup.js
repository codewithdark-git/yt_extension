console.log('Popup Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    const sentimentButton = document.getElementById('fetch-sentiment');
    const blogButton = document.getElementById('generate-blog');
    const qaButton = document.getElementById('get-answer');
    const wordCloudButton = document.getElementById('generate-word-cloud');
    const wordCloudImage = document.getElementById('word-cloud-image');
    const statusDot = document.querySelector('.dot');
    const statusText = document.getElementById('status-text');
    let currentVideoId = null;

    function updateConnectionStatus(connected, message) {
        statusDot.className = connected ? 'dot connected' : 'dot';
        statusText.textContent = message;
    }

    function updateUI(videoId) {
        console.log('Updating UI with video ID:', videoId);
        currentVideoId = videoId;
        
        const hasVideoId = videoId !== null;
        const buttons = [sentimentButton, blogButton, qaButton, wordCloudButton];
        
        buttons.forEach(button => {
            button.disabled = !hasVideoId;
            if (hasVideoId) {
                button.classList.remove('loading');
            }
        });

        if (!hasVideoId) {
            updateConnectionStatus(false, 'No YouTube video detected');
            document.querySelectorAll('.result-box').forEach(box => {
                box.textContent = 'Please navigate to a YouTube video';
            });
        } else {
            updateConnectionStatus(true, 'Connected to video');
        }
    }

    // Check if we're on YouTube and get video ID
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const url = tabs[0].url;
        if (url && url.includes('youtube.com/watch')) {
            const urlObj = new URL(url);
            const videoId = urlObj.searchParams.get('v');
            if (videoId) {
                updateUI(videoId);
            } else {
                updateConnectionStatus(false, 'No video ID found');
            }
        } else {
            updateConnectionStatus(false, 'Not on YouTube');
        }
    });

    sentimentButton.addEventListener('click', function() {
        if (!currentVideoId) return;
        
        const resultBox = document.getElementById('sentiment-result');
        const wordCloudImage = document.getElementById('word-cloud-image');
        resultBox.textContent = 'Analyzing sentiment...';
        wordCloudImage.style.display = 'none';
        sentimentButton.classList.add('loading');
        
        // Parallel requests for sentiment and word cloud
        Promise.all([
            fetch('http://localhost:8000/sentiment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: currentVideoId })
            }),
            fetch('http://localhost:8000/word-cloud', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: currentVideoId })
            })
        ])
        .then(responses => Promise.all(responses.map(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })))
        .then(([sentimentData, wordCloudData]) => {
            // Display sentiment text
            resultBox.textContent = sentimentData.sentiment;
            resultBox.style.whiteSpace = 'pre-wrap';

            // Display word cloud image
            wordCloudImage.src = `data:image/png;base64,${wordCloudData.word_cloud}`;
            wordCloudImage.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            resultBox.textContent = 'Error analyzing sentiment and generating word cloud';
            wordCloudImage.style.display = 'none';
        })
        .finally(() => {
            sentimentButton.classList.remove('loading');
        });
    });

    const copyBlogButton = document.getElementById('copy-blog');
    const copyAnswerButton = document.getElementById('copy-answer');
    let fullBlogPost = '';
    let fullAnswer = '';

    function createPreview(text, maxLines = 3) {
        const lines = text.split('\n');
        const preview = lines.slice(0, maxLines).join('\n');
        return preview + (lines.length > maxLines ? '...' : '');
    }

    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.querySelector('.button-text').textContent;
            button.querySelector('.button-text').textContent = 'Copied!';
            button.classList.add('copy-success');
            
            setTimeout(() => {
                button.querySelector('.button-text').textContent = originalText;
                button.classList.remove('copy-success');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }

    copyBlogButton.addEventListener('click', () => copyToClipboard(fullBlogPost, copyBlogButton));
    copyAnswerButton.addEventListener('click', () => copyToClipboard(fullAnswer, copyAnswerButton));

    blogButton.addEventListener('click', function() {
        if (!currentVideoId) return;
        
        const resultBox = document.getElementById('blog-result');
        const previewBox = document.getElementById('blog-preview');
        const tone = document.getElementById('blog-tone').value;
        const length = document.getElementById('blog-length').value;
        
        resultBox.textContent = 'Generating blog post...';
        previewBox.textContent = '';
        copyBlogButton.style.display = 'none';
        blogButton.classList.add('loading');
        
        fetch('http://localhost:8000/blog', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_id: currentVideoId,
                tone: tone,
                length: length
            })
        })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                fullBlogPost = data.blog_post;
                previewBox.textContent = createPreview(data.blog_post);
                resultBox.style.display = 'none';
                copyBlogButton.style.display = 'flex';
            })
            .catch(error => {
                console.error('Error:', error);
                resultBox.textContent = 'Error generating blog post';
                previewBox.textContent = '';
            })
            .finally(() => {
                blogButton.classList.remove('loading');
            });
    });

    qaButton.addEventListener('click', function() {
        if (!currentVideoId) return;
        
        const question = document.getElementById('question-input').value;
        if (!question.trim()) {
            document.getElementById('answer-result').textContent = 'Please enter a question';
            return;
        }
        
        const resultBox = document.getElementById('answer-result');
        const previewBox = document.getElementById('answer-preview');
        resultBox.textContent = 'Getting answer...';
        previewBox.textContent = '';
        copyAnswerButton.style.display = 'none';
        qaButton.classList.add('loading');
        
        fetch('http://localhost:8000/question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_id: currentVideoId,
                question: question
            })
        })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                fullAnswer = data.answer;
                previewBox.textContent = createPreview(data.answer);
                resultBox.style.display = 'none';
                copyAnswerButton.style.display = 'flex';
            })
            .catch(error => {
                console.error('Error:', error);
                resultBox.textContent = 'Error getting answer';
                previewBox.textContent = '';
            })
            .finally(() => {
                qaButton.classList.remove('loading');
            });
    });
});  // End of DOMContentLoaded event listener
