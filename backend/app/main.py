import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .llm import answer_from_context
from .models import AnswerResponse, ChatRequest, Source, VideoRequest
from .rag import cache
from .youtube import fetch_transcript, get_video_id

load_dotenv()
app = FastAPI(title="YouTube Video Chat API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.getenv("ALLOWED_ORIGIN", r"chrome-extension://.*"),
    allow_methods=["*"],
    allow_headers=["*"],
)


def retrieve(video_url: str, question: str) -> tuple[str, list]:
    try:
        video_id = get_video_id(video_url)
        index = cache.get_or_create(video_id, fetch_transcript(video_id))
        return video_id, index.search(question)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Could not read this video's captions: {error}") from error


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=AnswerResponse)
def chat(request: ChatRequest):
    video_id, chunks = retrieve(request.video_url, request.question)
    try:
        answer = answer_from_context(request.question, chunks)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"The AI answer request failed: {error}") from error
    return AnswerResponse(video_id=video_id, answer=answer, sources=[Source(start=c.start, end=c.end, text=c.text) for c in chunks])


@app.post("/summarize", response_model=AnswerResponse)
def summarize(request: VideoRequest):
    return chat(ChatRequest(video_url=request.video_url, question="Give a short, beginner-friendly summary of this video. Include 3 to 5 key takeaways."))
