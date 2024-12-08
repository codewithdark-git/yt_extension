# yt_extension

## Project Title
YouTube Video Analysis Chrome Extension

## Project Overview
A Chrome extension that analyzes YouTube videos, providing sentiment analysis, blog post generation, Q&A capabilities, and visual representations through word clouds.

## Features
- **Sentiment Analysis**: Extracts sentiment from video transcripts and provides insights.
- **Blog Post Generation**: Generates customizable blog posts based on video content.
- **Q&A System**: Allows users to ask questions about video content and retrieves answers.
- **Word Cloud Visualization**: Creates a visual representation of frequently used words in the transcript.

## Technical Architecture
- **Frontend**: Chrome Extension (Manifest V3)
- **Backend**: FastAPI with Python
- **Communication**: REST API calls to localhost:8000

## Installation
1. Clone the repository.
2. Navigate to the project directory.
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start the FastAPI server:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   OR
   .\run_api.bat
   ```
2. Load the Chrome extension in your browser by navigating to `chrome://extensions`, enabling "Developer mode," and clicking "Load unpacked." Select the `chrome_extension` directory.
3. Navigate to a YouTube video, click the extension icon, and use the available features.

## Contributing
Feel free to submit issues or pull requests.

## License
This project is licensed under the MIT License.
