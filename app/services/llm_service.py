from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import logging
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama3-8b-8192",
            temperature=0.7,
            max_tokens=4096  # Set a lower max tokens to prevent context length issues
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reduced chunk size
            chunk_overlap=50,  # Reduced overlap
            length_function=len
        )

    def create_vector_store(self, text: str) -> FAISS:
        try:
            chunks = self.text_splitter.split_text(text)
            return FAISS.from_texts(chunks, self.embeddings)
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def generate_blog_post(self, transcript: str, tone: str = "informative", length: str = "medium") -> str:
        try:
            word_counts = {
                "short": 600,
                "medium": 1200,
                "long": 1800
            }
            
            # Split transcript into chunks if it's too long
            if len(transcript) > 4000:
                chunks = self.text_splitter.split_text(transcript)
                # Take the first few chunks that fit within context window
                transcript = " ".join(chunks[:4])
            
            messages = [
                SystemMessage(content="You are a professional blog writer who creates engaging and well-structured content."),
                HumanMessage(content=f"""
                Generate a {length} blog post (approximately {word_counts[length]} words) 
                in a {tone} tone based on the following transcript.
                
                Guidelines:
                1. Write an engaging introduction that hooks the reader
                2. Break down the content into clear, logical sections with headings
                3. Include relevant examples and key points from the video
                4. Add a conclusion that summarizes the main takeaways
                5. Maintain the specified {tone} tone throughout
                6. Format the text with proper markdown
                
                Transcript: {transcript}
                """)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating blog post: {str(e)}")
            raise

    def answer_question(self, question: str, transcript: str) -> str:
        try:
            vector_store = self.create_vector_store(transcript)
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True,
                verbose=True
            )
            
            response = qa_chain({"query": question})
            return response["result"]
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise

    def analyze_sentiment(self, transcript: str) -> dict:
        try:
            # Truncate transcript if too long
            max_length = 4000
            if len(transcript) > max_length:
                transcript = transcript[:max_length] + "..."
            
            messages = [
                SystemMessage(content="""
                You are a sentiment analysis expert. Analyze the sentiment of video transcripts 
                and provide detailed insights. Return the analysis in the following JSON format:
                {
                    "sentiment": "positive" or "negative",
                    "confidence": "high" or "medium" or "low",
                    "summary": "brief explanation of the sentiment"
                }
                """),
                HumanMessage(content=f"""
                Analyze the sentiment of this video transcript. Consider:
                - Speaker's tone and word choice
                - Overall message and themes
                - Emotional elements
                - Key phrases and expressions
                
                Transcript: {transcript}
                """)
            ]
            
            response = self.llm.invoke(messages)
            
            # Extract sentiment from response
            content = response.content.strip().lower()
            
            # Default response if parsing fails
            result = {
                "sentiment": "positive" if "positive" in content else "negative",
                "confidence": "medium",
                "summary": content[:100] + "..."
            }
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            raise ValueError(f"Failed to analyze sentiment: {str(e)}")

    def generate_word_cloud(self, transcript: str) -> str:
        try:
            # Preprocess the transcript
            def preprocess_text(text):
                # Convert to lowercase and remove special characters
                text = text.lower()
                text = re.sub(r'[^\w\s]', '', text)
                
                # Remove common stop words
                stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after'])
                words = [word for word in text.split() if word not in stop_words]
                
                return ' '.join(words)

            preprocessed_text = preprocess_text(transcript)

            # Generate word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                min_font_size=10
            ).generate(preprocessed_text)

            # Create a matplotlib figure
            plt.figure(figsize=(10,5), facecolor=None)
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.tight_layout(pad=0)

            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()

            # Encode to base64
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating word cloud: {str(e)}")
            raise ValueError(f"Failed to generate word cloud: {str(e)}")
