"""
Job Description Routes.
Handles creation, retrieval, and management of job postings.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database.connection import get_database
from app.models.job import JobCreate, JobBase
from app.services.text_cleaning import clean_text
from app.services.skill_extractor import extract_skills
from app.services.embedding import generate_embedding

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobBase):
    """
    Create a new job description.
    Extracts skills and generates embedding automatically.
    """
    try:
        # Clean text
        cleaned = clean_text(job.description)

        # Extract skills from job description
        extracted_skills = extract_skills(job.description, is_job=True)
        all_skills = list(set(job.required_skills or []) | set(extracted_skills))

        # Generate embedding
        embedding = generate_embedding(cleaned or job.description)

        # Store in MongoDB
        db = get_database()
        job_doc = {
            "title": job.title,
            "description": job.description,
            "cleaned_text": cleaned,
            "required_skills": all_skills,
            "company": job.company,
            "location": job.location,
            "embedding": embedding,
        }
        result = await db["jobs"].insert_one(job_doc)

        return {
            "success": True,
            "job_id": str(result.inserted_id),
            "title": job.title,
            "required_skills": all_skills,
            "skill_count": len(all_skills),
        }

    except Exception as e:
        logger.error(f"Job creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}",
        )


@router.get("/")
async def list_jobs():
    """List all job descriptions."""
    db = get_database()
    jobs = []
    async for doc in db["jobs"].find({}, {"embedding": 0, "cleaned_text": 0}):
        doc["id"] = str(doc.pop("_id"))
        jobs.append(doc)
    return {"jobs": jobs, "total": len(jobs)}


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get a specific job by ID."""
    db = get_database()
    try:
        doc = await db["jobs"].find_one(
            {"_id": ObjectId(job_id)}, {"embedding": 0}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")

    doc["id"] = str(doc.pop("_id"))
    return doc


@router.put("/{job_id}")
async def update_job(job_id: str, job: JobBase):
    """Update an existing job description."""
    db = get_database()
    try:
        cleaned = clean_text(job.description)
        extracted_skills = extract_skills(job.description, is_job=True)
        all_skills = list(set(job.required_skills or []) | set(extracted_skills))
        embedding = generate_embedding(cleaned or job.description)

        result = await db["jobs"].update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "title": job.title,
                    "description": job.description,
                    "cleaned_text": cleaned,
                    "required_skills": all_skills,
                    "company": job.company,
                    "location": job.location,
                    "embedding": embedding,
                }
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"success": True, "message": "Job updated"}


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job description."""
    db = get_database()
    try:
        result = await db["jobs"].delete_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"success": True, "message": "Job deleted"}
