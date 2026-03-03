"""
CV Upload Routes.
Handles file upload, text extraction, and candidate storage.
"""

import logging
import traceback
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from bson import ObjectId

from app.database.connection import get_database
from app.services.parser import extract_text
from app.services.text_cleaning import clean_text, detect_language
from app.services.skill_extractor import extract_skills
from app.services.embedding import generate_embedding

logger = logging.getLogger(__name__)
router = APIRouter()

# Max file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


@router.post("/cv", status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(""),
):
    """
    Upload a CV file (PDF or DOCX).
    Extracts text, detects language, extracts skills, generates embedding.
    Stores candidate in MongoDB.
    """
    try:
        logger.info(f"Received upload request for: {file.filename}")

        # Validate file type
        if file.content_type not in ALLOWED_TYPES and not file.filename.endswith(
            (".pdf", ".docx", ".doc")
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are supported.",
            )

        # Read file bytes
        try:
            file_bytes = await file.read()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise HTTPException(status_code=400, detail="Failed to read file upload.")

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10 MB limit.",
            )

        # 1. Extract raw text
        try:
            logger.info("Extracting text...")
            raw_text = extract_text(file_bytes, file.filename)
            if not raw_text or not raw_text.strip():
                logger.warning("Empty text extracted from CV.")
                raise ValueError("Could not extract any text from the file.")
        except Exception as e:
            logger.error(f"Text extraction failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Text extraction failed: {str(e)}",
            )

        # 2. Detect language
        try:
            language = detect_language(raw_text)
        except Exception:
            language = "en"

        # 3. Clean text
        try:
            cleaned = clean_text(raw_text, language)
        except Exception as e:
            logger.error(f"Text cleaning failed: {e}")
            cleaned = raw_text  # Fallback

        # 4. Extract skills (Non-fatal)
        try:
            logger.info("Extracting skills...")
            skills = extract_skills(raw_text)
        except Exception as e:
            logger.error(f"Skill extraction failed: {traceback.format_exc()}")
            print(f"SKILL EXTRACTION ERROR: {e}") # Force print
            skills = []

        # 5. Generate embedding
        try:
            logger.info("Generating embedding...")
            embedding = generate_embedding(cleaned or raw_text)
        except Exception as e:
             logger.error(f"Embedding failed: {traceback.format_exc()}")
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail=f"Embedding generation failed: {str(e)}",
             )

        # 6. Store in MongoDB
        try:
            db = get_database()
            candidate_doc = {
                "name": name,
                "email": email,
                "cv_text": raw_text,
                "cleaned_text": cleaned,
                "skills": skills,
                "embedding": embedding,
                "language": language,
                "filename": file.filename,
                "score": None,
            }
            logger.info("Inserting into MongoDB...")
            result = await db["candidates"].insert_one(candidate_doc)
            logger.info(f"Inserted candidate ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Database insertion failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

        return {
            "success": True,
            "candidate_id": str(result.inserted_id),
            "name": name,
            "language": language,
            "skills": skills,
            "skill_count": len(skills),
            "text_preview": raw_text[:300] + "..." if len(raw_text) > 300 else raw_text,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled Upload Error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed unexpectedly: {str(e)}",
        )


@router.get("/candidates")
async def list_candidates():
    """List all uploaded candidates."""
    try:
        db = get_database()
        candidates = []
        async for doc in db["candidates"].find({}, {"embedding": 0, "cleaned_text": 0}):
            doc["id"] = str(doc.pop("_id"))
            candidates.append(doc)
        return {"candidates": candidates, "total": len(candidates)}
    except Exception as e:
        logger.error(f"List candidates failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list candidates")


@router.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get a specific candidate by ID."""
    try:
        db = get_database()
        doc = await db["candidates"].find_one(
            {"_id": ObjectId(candidate_id)}, {"embedding": 0}
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Candidate not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete a candidate by ID."""
    try:
        db = get_database()
        result = await db["candidates"].delete_one({"_id": ObjectId(candidate_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"success": True, "message": "Candidate deleted"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
