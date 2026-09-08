from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class DocumentChunkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_size_bytes: int
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    fact_count: Optional[int] = 0

class DocumentDetailResponse(DocumentResponse):
    pass

class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    error_message: Optional[str] = None
    page_count: int
    fact_count: int
