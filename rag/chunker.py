import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Document:
    content: str
    company: str
    year: str
    source: str
    chunk_id: str
    page: Optional[int] = None


class TextChunker:
    """Handles semantic text chunking"""

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, company: str, year: str, source: str) -> List[Document]:
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks: List[Document] = []
        current_chunk = ""
        current_size = 0
        chunk_id = 0

        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_size + sentence_size > self.chunk_size and current_chunk:
                doc = Document(
                    content=current_chunk.strip(),
                    company=company,
                    year=year,
                    source=source,
                    chunk_id=f"{company}_{year}_{chunk_id}"
                )
                chunks.append(doc)

                words = current_chunk.split()
                overlap_text = ' '.join(words[-self.overlap:]) if len(words) > self.overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_size = len(current_chunk.split())
                chunk_id += 1
            else:
                current_chunk += " " + sentence
                current_size += sentence_size

        if current_chunk.strip():
            doc = Document(
                content=current_chunk.strip(),
                company=company,
                year=year,
                source=source,
                chunk_id=f"{company}_{year}_{chunk_id}"
            )
            chunks.append(doc)

        return chunks


