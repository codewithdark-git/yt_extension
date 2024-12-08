from pydantic import BaseModel, Field
from typing import Optional

class TranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")

class BlogRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    tone: str = Field(..., description="Desired tone of the blog post (formal, casual, informative)")
    length: str = Field(..., description="Desired length of the blog post (short, medium, long)")

class QuestionRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    question: str = Field(..., description="Question about the video content")

class TranscriptResponse(BaseModel):
    transcript: str = Field(..., description="Video transcript text")

class BlogResponse(BaseModel):
    blog_post: str = Field(..., description="Generated blog post")

class QuestionResponse(BaseModel):
    answer: str = Field(..., description="Answer to the question")
