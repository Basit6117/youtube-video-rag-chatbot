import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


@dataclass(frozen=True)
class TranscriptSegment:
    text: str
    start: float
    duration: float


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def get_video_id(video_url: str) -> str:
    parsed = urlparse(video_url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/", "/live/")):
            candidate = parsed.path.strip("/").split("/")[1]
        else:
            candidate = ""
    else:
        candidate = ""
    if not VIDEO_ID_PATTERN.fullmatch(candidate):
        raise ValueError("Please open a valid YouTube video before using Video Chat.")
    return candidate


def fetch_transcript(video_id: str) -> list[TranscriptSegment]:
    """Retrieve an English transcript, falling back to YouTube's best available track."""
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=["en"])
    except Exception:
        fetched = api.fetch(video_id)

    segments = []
    for item in fetched:
        # The library returns FetchedTranscriptSnippet objects in current versions.
        text = getattr(item, "text", None) or item["text"]
        start = getattr(item, "start", None)
        if start is None:
            start = item["start"]
        duration = getattr(item, "duration", None)
        if duration is None:
            duration = item.get("duration", 0)
        segments.append(TranscriptSegment(text=text, start=float(start), duration=float(duration)))
    if not segments:
        raise ValueError("This video has no usable captions.")
    return segments
