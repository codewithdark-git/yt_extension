import streamlit as st
import requests

# Set up the Streamlit app
st.set_page_config(
    page_title="YouTube Extension",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define the backend API endpoints
API_BASE_URL = "http://localhost:8000"
BLOG_POST_ENDPOINT = f"{API_BASE_URL}/blog_post"
QA_ENDPOINT = f"{API_BASE_URL}/question_answer"
SENTIMENT_ENDPOINT = f"{API_BASE_URL}/sentiment"

# Function to display sentiment analysis
st.title("Sentiment Analysis")
response = requests.get(SENTIMENT_ENDPOINT)
if response.status_code == 200:
    sentiment_data = response.json()
    st.write("Sentiment:", sentiment_data.get('sentiment'))
else:
    st.error("Failed to fetch sentiment analysis.")

# Function to generate a blog post
st.header("Generate Blog Post")
blog_input = st.text_area("Enter your blog topic:")
if st.button("Generate Blog Post"):
    response = requests.post(BLOG_POST_ENDPOINT, json={"topic": blog_input})
    if response.status_code == 200:
        blog_post = response.json().get('blog_post')
        st.write(blog_post)
    else:
        st.error("Failed to generate blog post.")

# Function for Question & Answer
st.header("Question & Answer")
question_input = st.text_input("Ask a question:")
if st.button("Get Answer"):
    response = requests.post(QA_ENDPOINT, json={"question": question_input})
    if response.status_code == 200:
        answer = response.json().get('answer')
        st.write(answer)
    else:
        st.error("Failed to get answer.")
