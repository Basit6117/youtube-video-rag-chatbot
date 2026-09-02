import os

from google import genai

from .rag import Chunk


def answer_from_context(question: str, chunks: list[Chunk]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to backend/.env and restart the server.")
    context = "\n\n".join(f"[{format_timestamp(c.start)}] {c.text}" for c in chunks)
    prompt = f"""You are a friendly video-learning assistant. Answer in simple, beginner-friendly language.
Use only the transcript excerpts below. If the answer is not supported by them, say: "I couldn't find that in this video's captions."
Do not invent facts. Mention relevant timestamps in your answer when useful.

Transcript excerpts:
{context}

User question: {question}
"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"), contents=prompt)
    return response.text or "I couldn't generate an answer from this video's captions."


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    minutes, seconds = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"
