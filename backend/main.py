from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import Optional
import aiofiles
import os
import time
import logging
from pathlib import Path

from config import settings
from database import get_db
from models import User, Course, Document
from schemas import (
    HealthResponse,
    UploadResponse,
    ProcessNoteResponse,
    MultiAgentProcessNoteResponse,
    QAItemResponse,
    KnowledgeCardResponse,
    RelatedNoteResponse,
    MultiAgentMetadata,
)
from services.ocr_service import ocr_service
from services.llm_service import llm_service
from services.auth_service import get_current_user, get_current_user_optional
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
from routes import user_router, courses_router, documents_router
from agents.graph import process_note_with_agents
from agents.state import ProcessingStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan event handler
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting up application...")
    # Ensure upload directory exists
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Database ready")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="DocuLens AI API",
    description="AI-powered note processing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(courses_router)
app.include_router(documents_router)

@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 健康检查"""
    return HealthResponse(
        status="healthy",
        message="AI Note Processing API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )

@app.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片文件
    
    Args:
        file: 上传的图片文件
    
    Returns:
        UploadResponse: 上传结果
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="只支持图片文件"
            )
        
        # 读取文件内容
        contents = await file.read()
        
        # 验证文件大小
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024}MB)"
            )
        
        # 生成唯一文件名
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        logger.info(f"文件上传成功: {filename}")
        
        return UploadResponse(
            filename=filename,
            message="文件上传成功",
            file_path=file_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """
    对上传的图片进行 OCR 识别
    
    Args:
        file: 上传的图片文件
    
    Returns:
        OCRResponse: OCR 识别结果
    """
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 调用 OCR 服务
        text, confidence = ocr_service.extract_text(contents)
        
        return {
            "success": True,
            "text": text,
            "confidence": confidence,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"OCR 处理失败: {str(e)}")
        return {
            "success": False,
            "text": "",
            "confidence": 0.0,
            "error": str(e)
        }

@app.post("/process-note", response_model=ProcessNoteResponse)
async def process_note(
    file: UploadFile = File(...),
    additional_context: str = Form(None),
    course_id: str = Form(None),
    title: str = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Complete note processing pipeline: Upload -> OCR -> LLM formatting -> Save to database

    Authentication is optional. If authenticated and course_id is provided, documents are saved.
    If not authenticated, only OCR + LLM formatting is performed (no RAG, no saving).

    Args:
        file: Image file to process
        additional_context: Additional context for LLM (optional)
        course_id: Course ID to save the document to (optional)
        title: Document title (optional, generated from content if not provided)
        current_user: Current authenticated user (injected, optional)
        db: Database session (injected)

    Returns:
        ProcessNoteResponse: Processing result with document ID (if saved)
    """
    start_time = time.time()
    saved_file_path = None

    try:
        user_email = current_user.email if current_user else "anonymous"
        logger.info(f"Processing note for user {user_email}: {file.filename}")

        # 1. Read file
        contents = await file.read()

        # Save uploaded file
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{file.filename}"
        saved_file_path = os.path.join(settings.upload_dir, filename)

        async with aiofiles.open(saved_file_path, 'wb') as f:
            await f.write(contents)

        # 2. OCR recognition
        logger.info("Step 1: OCR processing...")
        ocr_text, confidence = ocr_service.extract_text(contents)

        if not ocr_text or len(ocr_text.strip()) < 10:
            raise Exception("OCR failed or text content too short")

        logger.info(f"OCR completed, extracted {len(ocr_text)} characters, confidence: {confidence:.2f}")

        # Determine if we should use RAG and save document
        use_rag = current_user and course_id
        course = None
        historical_context = []
        document_id = None

        if use_rag:
            # Verify course exists and belongs to user
            course = db.query(Course).filter(
                Course.id == course_id,
                Course.user_id == current_user.id
            ).first()

            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # 3. RAG: Get historical context from similar notes
            logger.info("Step 2: Generating embedding for context retrieval...")
            embedding_service = get_embedding_service()
            query_embedding = embedding_service.create_embedding(ocr_text)

            logger.info("Step 3: Retrieving historical context...")
            vector_store = get_vector_store()
            historical_context = vector_store.get_context_for_new_note(
                db=db,
                new_note_text=ocr_text,
                new_note_embedding=query_embedding,
                course_id=course_id,
                top_k=3  # Retrieve top 3 relevant historical notes
            )

            # 4. LLM formatting with RAG enhancement
            logger.info(f"Step 4: LLM formatting with RAG ({len(historical_context)} historical notes)...")
            if historical_context:
                # Use RAG-enhanced formatting
                formatted_note = llm_service.format_note_with_rag(
                    ocr_text=ocr_text,
                    course_name=course.name,
                    historical_context=historical_context,
                    additional_context=additional_context
                )
            else:
                # Fallback to basic formatting if no historical context
                logger.info("No historical context found, using basic formatting")
                formatted_note = llm_service.format_note(ocr_text, additional_context)

            # 5. Save to database
            # Generate title from formatted note if not provided
            if not title:
                # Extract first line or first 50 characters as title
                lines = formatted_note.split('\n')
                title = lines[0].strip('#').strip()[:100] if lines else "Untitled Note"

            # Create excerpt from formatted note
            excerpt = formatted_note[:200]

            # Generate embedding for the formatted note
            final_embedding = embedding_service.create_embedding(formatted_note)

            # Create document
            document = Document(
                course_id=course_id,
                user_id=current_user.id,
                title=title,
                original_text=ocr_text,
                formatted_note=formatted_note,
                excerpt=excerpt,
                image_path=saved_file_path,
                processing_time=time.time() - start_time,
                embedding=final_embedding,
                doc_metadata={
                    "ocr_confidence": confidence,
                    "file_name": file.filename,
                    "context": additional_context,
                    "rag_context_count": len(historical_context)
                }
            )

            db.add(document)
            db.commit()
            db.refresh(document)
            document_id = str(document.id)
            logger.info(f"Document saved: {document_id}")
        else:
            # No RAG, just basic LLM formatting
            logger.info("Step 2: Basic LLM formatting (no RAG - not authenticated or no course)")
            formatted_note = llm_service.format_note(ocr_text, additional_context)
            logger.info("Skipping document save (no authentication or course)")

        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f}s")

        return ProcessNoteResponse(
            success=True,
            original_text=ocr_text,
            formatted_note=formatted_note,
            processing_time=processing_time,
            document_id=document_id,
            error=None
        )

    except HTTPException:
        # Clean up file if it was saved
        if saved_file_path and os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        raise
    except Exception as e:
        # Clean up file if it was saved
        if saved_file_path and os.path.exists(saved_file_path):
            os.remove(saved_file_path)

        processing_time = time.time() - start_time
        logger.error(f"Processing failed: {str(e)}")

        return ProcessNoteResponse(
            success=False,
            original_text="",
            formatted_note="",
            processing_time=processing_time,
            document_id=None,
            error=str(e)
        )

@app.delete("/uploads/{filename}")
async def delete_upload(filename: str):
    """
    删除上传的文件

    Args:
        filename: 文件名
    """
    try:
        file_path = os.path.join(settings.upload_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        os.remove(file_path)
        logger.info(f"文件删除成功: {filename}")

        return {"message": "文件删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-note-agents", response_model=MultiAgentProcessNoteResponse)
async def process_note_with_multi_agents(
    file: UploadFile = File(...),
    additional_context: str = Form(None),
    course_id: str = Form(None),
    title: str = Form(None),
    generate_qa: bool = Form(True),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Process note using the Multi-Agent System (Phase 5).

    This endpoint uses a LangGraph-based multi-agent workflow to process notes:
    - OCR Agent: Extract and correct text from image
    - Structure Agent: Analyze text structure and key concepts
    - Content Agent: Integrate RAG context and enhance content
    - QA Agent: Generate review questions and knowledge cards
    - Integration Agent: Assemble final formatted note

    Compared to /process-note, this provides:
    - More structured analysis
    - Q&A generation
    - Knowledge cards
    - Key concept extraction
    - Better error handling

    Args:
        file: Image file to process
        additional_context: Additional context for LLM (optional)
        course_id: Course ID for RAG context (optional)
        title: Document title (optional)
        generate_qa: Whether to generate Q&A materials (default: True)
        current_user: Current authenticated user (injected, optional)
        db: Database session (injected)

    Returns:
        MultiAgentProcessNoteResponse: Comprehensive processing result
    """
    saved_file_path = None

    try:
        user_email = current_user.email if current_user else "anonymous"
        logger.info(f"[Multi-Agent] Processing note for user {user_email}: {file.filename}")

        # 1. Read and save file
        contents = await file.read()

        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{file.filename}"
        saved_file_path = os.path.join(settings.upload_dir, filename)

        async with aiofiles.open(saved_file_path, 'wb') as f:
            await f.write(contents)

        # 2. Get course info if provided
        course_name = None
        if current_user and course_id:
            course = db.query(Course).filter(
                Course.id == course_id,
                Course.user_id == current_user.id
            ).first()
            if course:
                course_name = course.name
            else:
                logger.warning(f"Course {course_id} not found for user {current_user.id}")
                course_id = None  # Reset course_id if not found

        # 3. Run multi-agent processing
        logger.info("[Multi-Agent] Starting multi-agent workflow...")
        final_state = await process_note_with_agents(
            image_bytes=contents,
            course_id=course_id,
            course_name=course_name,
            additional_context=additional_context,
            user_id=str(current_user.id) if current_user else None,
            generate_qa=generate_qa
        )

        # 4. Check if processing succeeded
        status = final_state.get("status", ProcessingStatus.FAILED)
        success = status == ProcessingStatus.COMPLETED

        if not success:
            errors = final_state.get("errors", [])
            error_msg = "; ".join(errors) if errors else "Processing failed"
            logger.error(f"[Multi-Agent] Processing failed: {error_msg}")
            return MultiAgentProcessNoteResponse(
                success=False,
                original_text=final_state.get("ocr_raw_text", ""),
                corrected_text=final_state.get("ocr_corrected_text", ""),
                final_note=final_state.get("final_note", ""),
                error=error_msg
            )

        # 5. Save document if authenticated with course
        document_id = None
        if current_user and course_id:
            try:
                final_note = final_state.get("final_note", "")
                ocr_text = final_state.get("ocr_raw_text", "")
                metadata = final_state.get("final_metadata", {})

                # Generate title if not provided
                if not title:
                    lines = final_note.split('\n')
                    title = lines[0].strip('#').strip()[:100] if lines else "Untitled Note"

                # Create excerpt
                excerpt = final_note[:200]

                # Generate embedding
                embedding_service = get_embedding_service()
                final_embedding = embedding_service.create_embedding(final_note)

                # Create document
                document = Document(
                    course_id=course_id,
                    user_id=current_user.id,
                    title=title,
                    original_text=ocr_text,
                    formatted_note=final_note,
                    excerpt=excerpt,
                    image_path=saved_file_path,
                    processing_time=metadata.get("processing_time_total", 0),
                    embedding=final_embedding,
                    doc_metadata={
                        "ocr_confidence": final_state.get("ocr_confidence", 0),
                        "file_name": file.filename,
                        "context": additional_context,
                        "multi_agent": True,
                        "agents_run": metadata.get("agents_run", []),
                        "qa_count": metadata.get("qa_items_count", 0),
                        "rag_context_count": metadata.get("related_notes_count", 0)
                    }
                )

                db.add(document)
                db.commit()
                db.refresh(document)
                document_id = str(document.id)
                logger.info(f"[Multi-Agent] Document saved: {document_id}")

            except Exception as save_error:
                logger.error(f"[Multi-Agent] Failed to save document: {save_error}")
                # Continue without saving

        # 6. Build response
        # Convert QA items
        qa_items = []
        for qa in final_state.get("qa_items", []):
            qa_items.append(QAItemResponse(
                question=getattr(qa, 'question', ''),
                answer=getattr(qa, 'answer', ''),
                difficulty=getattr(qa, 'difficulty', 'medium'),
                concept=getattr(qa, 'concept', None)
            ))

        # Convert knowledge cards
        knowledge_cards = []
        for card in final_state.get("knowledge_cards", []):
            knowledge_cards.append(KnowledgeCardResponse(
                front=getattr(card, 'front', ''),
                back=getattr(card, 'back', ''),
                tags=getattr(card, 'tags', []),
                concept=getattr(card, 'concept', None)
            ))

        # Convert related notes
        related_notes = []
        for note in final_state.get("related_notes", []):
            related_notes.append(RelatedNoteResponse(
                document_id=getattr(note, 'document_id', ''),
                title=getattr(note, 'title', ''),
                excerpt=getattr(note, 'excerpt', ''),
                similarity=getattr(note, 'similarity', 0),
                created_at=getattr(note, 'created_at', None)
            ))

        # Convert key concepts
        key_concepts = []
        for concept in final_state.get("key_concepts", []):
            key_concepts.append({
                "term": getattr(concept, 'term', str(concept)),
                "definition": getattr(concept, 'definition', None),
                "context": getattr(concept, 'context', None),
                "importance": getattr(concept, 'importance', 0.5)
            })

        # Build metadata response
        final_metadata = final_state.get("final_metadata", {})
        metadata_response = MultiAgentMetadata(
            processing_time_total=final_metadata.get("processing_time_total", 0),
            processing_times=final_metadata.get("processing_times", {}),
            ocr_confidence=final_metadata.get("ocr_confidence", 0),
            document_type=final_metadata.get("document_type", "notes"),
            related_notes_count=final_metadata.get("related_notes_count", 0),
            key_concepts_count=final_metadata.get("key_concepts_count", 0),
            qa_items_count=final_metadata.get("qa_items_count", 0),
            knowledge_cards_count=final_metadata.get("knowledge_cards_count", 0),
            special_contents_count=final_metadata.get("special_contents_count", 0),
            errors=final_metadata.get("errors", []),
            agents_run=final_metadata.get("agents_run", []),
            used_rag=final_metadata.get("used_rag", False),
            generated_qa=final_metadata.get("generated_qa", False),
            timestamp=final_metadata.get("timestamp", "")
        )

        logger.info(f"[Multi-Agent] Processing completed successfully in {metadata_response.processing_time_total:.2f}s")

        return MultiAgentProcessNoteResponse(
            success=True,
            original_text=final_state.get("ocr_raw_text", ""),
            corrected_text=final_state.get("ocr_corrected_text", ""),
            final_note=final_state.get("final_note", ""),
            qa_items=qa_items,
            knowledge_cards=knowledge_cards,
            key_points=final_state.get("key_points", []),
            related_notes=related_notes,
            key_concepts=key_concepts,
            metadata=metadata_response,
            document_id=document_id,
            error=None
        )

    except HTTPException:
        if saved_file_path and os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        raise
    except Exception as e:
        if saved_file_path and os.path.exists(saved_file_path):
            os.remove(saved_file_path)

        logger.error(f"[Multi-Agent] Processing failed with error: {str(e)}")

        return MultiAgentProcessNoteResponse(
            success=False,
            original_text="",
            corrected_text="",
            final_note="",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式下自动重载
    )