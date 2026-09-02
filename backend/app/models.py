from pydantic import BaseModel, Field


class VideoRequest(BaseModel):
    video_url: str = Field(min_length=8, description="A YouTube watch, short, or youtu.be URL")


class ChatRequest(VideoRequest):
    question: str = Field(min_length=2, max_length=2000)


class Source(BaseModel):
    start: float
    end: float
    text: str


class AnswerResponse(BaseModel):
    video_id: str
    answer: str
    sources: list[Source]
