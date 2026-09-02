from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .youtube import TranscriptSegment


@dataclass(frozen=True)
class Chunk:
    text: str
    start: float
    end: float


def make_chunks(segments: list[TranscriptSegment], max_characters: int = 1100, overlap_segments: int = 2) -> list[Chunk]:
    chunks: list[Chunk] = []
    current: list[TranscriptSegment] = []
    size = 0
    for segment in segments:
        if current and size + len(segment.text) > max_characters:
            chunks.append(Chunk(
                text=" ".join(s.text for s in current),
                start=current[0].start,
                end=current[-1].start + current[-1].duration,
            ))
            current = current[-overlap_segments:]
            size = sum(len(s.text) for s in current)
        current.append(segment)
        size += len(segment.text) + 1
    if current:
        chunks.append(Chunk(" ".join(s.text for s in current), current[0].start, current[-1].start + current[-1].duration))
    return chunks


class VideoIndex:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        # TF-IDF keeps the first release light and entirely local. It can later
        # be swapped for semantic embeddings without changing the API.
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(chunk.text for chunk in chunks)

    def search(self, question: str, k: int = 4) -> list[Chunk]:
        k = min(k, len(self.chunks))
        query = self.vectorizer.transform([question])
        scores = cosine_similarity(query, self.matrix).ravel()
        matches = scores.argsort()[::-1][:k]
        return [self.chunks[i] for i in matches]


class IndexCache:
    def __init__(self):
        self._indexes: dict[str, VideoIndex] = {}

    def get_or_create(self, video_id: str, segments: list[TranscriptSegment]) -> VideoIndex:
        if video_id not in self._indexes:
            self._indexes[video_id] = VideoIndex(make_chunks(segments))
        return self._indexes[video_id]


cache = IndexCache()
