import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.fact import Fact
from backend.app.schemas.document import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentStatusResponse
)
from backend.app.schemas.fact import FactResponse
from backend.app.services.pdf.extractor import PDFExtractor
from backend.app.services.pdf.chunker import DocumentChunker
from backend.app.services.extraction.fact_extractor import FactExtractorService
from backend.app.services.comparison.relationship_classifier import RelationshipClassifier

router = APIRouter(prefix="/documents", tags=["Documents"])

def process_document_task(document_id: str):
    """Background task to extract and chunk PDF, then extract facts."""
    from backend.app.core.database import SessionLocal
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = "EXTRACTING"
        db.commit()

        # Extract text page by page
        pages, issues = PDFExtractor.extract_pages(doc.file_path, max_pages=settings.MAX_PAGES_TO_PROCESS)
        doc.page_count = len(pages)
        db.commit()

        # Chunk pages
        chunker = DocumentChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        chunks = chunker.chunk_pages(pages)

        # Fact Extraction
        extractor = FactExtractorService(db)
        extractor.process_document_chunks(doc, chunks, issues)

        doc.status = "EXTRACTED"
        db.commit()

        # Auto-run cross-document analysis if multiple documents exist
        total_docs = db.query(Document).filter(Document.status.in_(["EXTRACTED", "COMPLETED"])).count()
        if total_docs >= 2:
            doc.status = "ANALYZING"
            db.commit()
            rel_classifier = RelationshipClassifier(db)
            rel_classifier.analyze_all_facts()

        doc.status = "COMPLETED"
        db.commit()
    except Exception as e:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload one or multiple PDF documents."""
    responses = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a PDF.")

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.filename}"
        save_path = settings.UPLOAD_DIR / safe_filename

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = save_path.stat().st_size

        doc = Document(
            id=doc_id,
            filename=file.filename,
            file_path=str(save_path),
            file_size_bytes=file_size,
            status="UPLOADED"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Queue background processing
        background_tasks.add_task(process_document_task, doc.id)

        responses.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_size_bytes=doc.file_size_bytes,
            page_count=doc.page_count,
            status=doc.status,
            error_message=doc.error_message,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            fact_count=0
        ))

    return responses


@router.post("/load-sample", response_model=List[DocumentResponse])
def load_sample_dataset(
    dataset_name: str,  # "delhivery" or "india-macroeconomy"
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Loads all PDFs from the curated starter dataset folder."""
    target_dir = settings.STARTER_DATASET_DIR / dataset_name
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail=f"Sample dataset '{dataset_name}' not found.")

    pdf_files = list(target_dir.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail=f"No PDF files found in '{dataset_name}'.")

    responses = []
    for pdf in sorted(pdf_files):
        # Check if already loaded
        existing = db.query(Document).filter(Document.filename == pdf.name).first()
        if existing:
            fact_count = db.query(func.count(Fact.id)).filter(Fact.document_id == existing.id).scalar()
            responses.append(DocumentResponse(
                id=existing.id,
                filename=existing.filename,
                file_size_bytes=existing.file_size_bytes,
                page_count=existing.page_count,
                status=existing.status,
                error_message=existing.error_message,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                fact_count=fact_count
            ))
            continue

        doc_id = str(uuid.uuid4())
        dest_path = settings.UPLOAD_DIR / f"{doc_id}_{pdf.name}"
        shutil.copy(pdf, dest_path)

        doc = Document(
            id=doc_id,
            filename=pdf.name,
            file_path=str(dest_path),
            file_size_bytes=dest_path.stat().st_size,
            status="UPLOADED"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        background_tasks.add_task(process_document_task, doc.id)

        responses.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_size_bytes=doc.file_size_bytes,
            page_count=doc.page_count,
            status=doc.status,
            error_message=doc.error_message,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            fact_count=0
        ))

    return responses


@router.get("", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """Return all uploaded documents with fact counts."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        fact_count = db.query(func.count(Fact.id)).filter(Fact.document_id == d.id).scalar() or 0
        results.append(DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_size_bytes=d.file_size_bytes,
            page_count=d.page_count,
            status=d.status,
            error_message=d.error_message,
            created_at=d.created_at,
            updated_at=d.updated_at,
            fact_count=fact_count
        ))
    return results


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Return metadata for a single document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    fact_count = db.query(func.count(Fact.id)).filter(Fact.document_id == doc.id).scalar() or 0
    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        file_size_bytes=doc.file_size_bytes,
        page_count=doc.page_count,
        status=doc.status,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        fact_count=fact_count
    )


@router.get("/{document_id}/pdf")
def get_document_pdf(document_id: str, db: Session = Depends(get_db)):
    """Serves the raw PDF file for in-browser inspection."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not Path(doc.file_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        filename=doc.filename
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """Return processing status of a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    fact_count = db.query(func.count(Fact.id)).filter(Fact.document_id == doc.id).scalar() or 0
    return DocumentStatusResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        error_message=doc.error_message,
        page_count=doc.page_count,
        fact_count=fact_count
    )


@router.post("/{document_id}/process")
def trigger_process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger or restart document processing."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    background_tasks.add_task(process_document_task, doc.id)
    return {"message": "Processing triggered", "document_id": doc.id, "status": "EXTRACTING"}


@router.get("/{document_id}/facts", response_model=List[FactResponse])
def get_document_facts(document_id: str, db: Session = Depends(get_db)):
    """Return all facts extracted from a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    facts = db.query(Fact).filter(Fact.document_id == document_id).order_by(Fact.evidence_page.asc()).all()
    results = []
    for f in facts:
        res = FactResponse.model_validate(f)
        res.document_name = doc.filename
        results.append(res)
    return results


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Deletes document and cascades deletion of chunks, facts, relationships."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove file from disk
    try:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully", "id": document_id}
