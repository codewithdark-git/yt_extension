from fastapi import APIRouter, Depends
from .models import (
    TranscriptRequest, BlogRequest, QuestionRequest,
    TranscriptResponse, BlogResponse, QuestionResponse
)
from .services.transcript_service import TranscriptService
from .services.llm_service import LLMService
from typing import Dict
from fastapi import HTTPException

router = APIRouter()

# Store video data in memory (in production, use a proper database)
video_data: Dict = {}

def get_llm_service():
    return LLMService()

def get_transcript_service():
    return TranscriptService()

@router.post("/transcript", response_model=TranscriptResponse)
async def fetch_transcript(
    request: TranscriptRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    transcript = transcript_service.get_transcript(request.video_id)
    
    # Create and store vector store for future use
    if request.video_id not in video_data:
        vector_store = llm_service.create_vector_store(transcript)
        video_data[request.video_id] = {
            "transcript": transcript,
            "vector_store": vector_store
        }
    
    return {"transcript": transcript}

@router.post("/blog", response_model=BlogResponse)
async def generate_blog(
    request: BlogRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    if request.video_id not in video_data:
        transcript = transcript_service.get_transcript(request.video_id)
        vector_store = llm_service.create_vector_store(transcript)
        video_data[request.video_id] = {
            "transcript": transcript,
            "vector_store": vector_store
        }
    
    blog_post = llm_service.generate_blog_post(
        video_data[request.video_id]["transcript"],
        request.tone,
        request.length
    )
    
    return {"blog_post": blog_post}

@router.post("/question", response_model=QuestionResponse)
async def answer_question(
    request: QuestionRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    try:
        # Get or create video data
        if request.video_id not in video_data:
            transcript = transcript_service.get_transcript(request.video_id)
            vector_store = llm_service.create_vector_store(transcript)
            video_data[request.video_id] = {
                "transcript": transcript,
                "vector_store": vector_store
            }
        
        # Get answer using the vector store
        answer = llm_service.answer_question(
            question=request.question,
            vector_store=video_data[request.video_id]["vector_store"]
        )
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

@router.post("/sentiment", response_model=dict)
async def analyze_sentiment(
    request: TranscriptRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    try:
        if request.video_id not in video_data:
            transcript = transcript_service.get_transcript(request.video_id)
            vector_store = llm_service.create_vector_store(transcript)
            video_data[request.video_id] = {
                "transcript": transcript,
                "vector_store": vector_store
            }
        
        sentiment_data = llm_service.analyze_sentiment(video_data[request.video_id]["transcript"])
        
        # Convert sentiment dictionary to a readable string
        sentiment_str = (
            f"Overall Sentiment: {sentiment_data['sentiment'].capitalize()}\n"
            f"Confidence: {sentiment_data['confidence'].capitalize()}\n"
            f"Summary: {sentiment_data['summary']}"
        )
        
        return {"sentiment": sentiment_str}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing sentiment: {str(e)}"
        )

@router.post("/word-cloud", response_model=dict)
async def generate_word_cloud(
    request: TranscriptRequest,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    try:
        if request.video_id not in video_data:
            transcript = transcript_service.get_transcript(request.video_id)
            vector_store = llm_service.create_vector_store(transcript)
            video_data[request.video_id] = {
                "transcript": transcript,
                "vector_store": vector_store
            }
        
        word_cloud_base64 = llm_service.generate_word_cloud(video_data[request.video_id]["transcript"])
        
        return {"word_cloud": word_cloud_base64}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating word cloud: {str(e)}"
        )
