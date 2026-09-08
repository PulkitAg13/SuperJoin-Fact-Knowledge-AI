import re
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunks pages into coherent passages while strictly preserving page numbers.
        Returns a list of chunks:
        [{
            'page_number': int,
            'chunk_index': int,
            'text': str,
            'char_start': int,
            'char_end': int
        }]
        """
        chunks = []
        global_chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            text = page["text"]

            if not text or len(text.strip()) == 0:
                continue

            # Split by double newline (paragraphs) or sentences
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
            if not paragraphs:
                paragraphs = [text.strip()]

            current_chunk = []
            current_len = 0
            page_char_start = 0

            for para in paragraphs:
                # If paragraph itself is larger than chunk size, split by sentences
                if len(para) > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if current_len + len(sent) > self.chunk_size and current_chunk:
                            chunk_text = " ".join(current_chunk)
                            chunks.append({
                                "page_number": page_num,
                                "chunk_index": global_chunk_idx,
                                "text": chunk_text,
                                "char_start": page_char_start,
                                "char_end": page_char_start + len(chunk_text)
                            })
                            global_chunk_idx += 1
                            # Retain overlap from end of current chunk
                            current_chunk = [sent]
                            current_len = len(sent)
                        else:
                            current_chunk.append(sent)
                            current_len += len(sent)
                else:
                    if current_len + len(para) > self.chunk_size and current_chunk:
                        chunk_text = "\n\n".join(current_chunk)
                        chunks.append({
                            "page_number": page_num,
                            "chunk_index": global_chunk_idx,
                            "text": chunk_text,
                            "char_start": page_char_start,
                            "char_end": page_char_start + len(chunk_text)
                        })
                        global_chunk_idx += 1
                        current_chunk = [para]
                        current_len = len(para)
                    else:
                        current_chunk.append(para)
                        current_len += len(para)

            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "page_number": page_num,
                    "chunk_index": global_chunk_idx,
                    "text": chunk_text,
                    "char_start": page_char_start,
                    "char_end": page_char_start + len(chunk_text)
                })
                global_chunk_idx += 1

        return chunks
