"""
Matching & Ranking Routes.
Core NLP matching logic: computes similarity scores, ranks candidates.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from bson import ObjectId

from app.database.connection import get_database
from app.models.job import MatchRequest, BulkMatchRequest
from app.services.similarity import compute_match_score, rank_candidates
from app.services.skill_extractor import compare_skills, extract_skills
from app.services.report_generator import generate_match_report

logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_candidate(db, candidate_id: str) -> dict:
    """Helper to fetch a candidate document."""
    try:
        doc = await db["candidates"].find_one({"_id": ObjectId(candidate_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return doc


async def _get_job(db, job_id: str) -> dict:
    """Helper to fetch a job document."""
    try:
        doc = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc


@router.post("/single")
async def match_single(request: MatchRequest):
    """
    Match a single candidate against a job description.

    Returns:
        match_score, matched_skills, missing_skills
    """
    db = get_database()
    candidate = await _get_candidate(db, request.candidate_id)
    job = await _get_job(db, request.job_id)

    # Validate embeddings exist
    if not candidate.get("embedding"):
        raise HTTPException(status_code=422, detail="Candidate has no embedding. Re-upload CV.")
    if not job.get("embedding"):
        raise HTTPException(status_code=422, detail="Job has no embedding. Re-create job.")

    # Compute cosine similarity score (Document Level - kept for reference or hybrid if needed)
    doc_score = compute_match_score(candidate["embedding"], job["embedding"])

    # Compare skills (Semantic & Normalized)
    cv_skills = candidate.get("skills", [])
    job_skills = job.get("required_skills", [])
    matched, missing, skill_score = compare_skills(cv_skills, job_skills)

    # Definitive Score: User requested "number_of_matched_skills / total_job_skills"
    # But usually a mix is safer?
    # User said: "match_score = number_of_matched_skills / total_job_skills * 100"
    # So we use skill_score as the MAIN score.
    final_score = skill_score

    # But if skills match is 0 (e.g. general job description), maybe fallback to doc score?
    if not job_skills and doc_score > 0:
        final_score = doc_score * 100 # Convert 0-1 to 0-100


    # Update candidate score in DB
    await db["candidates"].update_one(
        {"_id": ObjectId(request.candidate_id)},
        {"$set": {"score": final_score}},
    )

    return {
        "candidate_id": request.candidate_id,
        "candidate_name": candidate["name"],
        "job_id": request.job_id,
        "job_title": job["title"],
        "match_score": final_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "cv_skills": cv_skills,
        "job_skills": job_skills,
        "language": candidate.get("language", "en"),
    }


@router.post("/bulk")
async def match_bulk(request: BulkMatchRequest):
    """
    Match multiple candidates (or all) against a job description.
    Returns ranked list of candidates by match score.
    """
    db = get_database()
    job = await _get_job(db, request.job_id)

    if not job.get("embedding"):
        raise HTTPException(status_code=422, detail="Job has no embedding.")

    # Fetch candidates
    if request.candidate_ids:
        # Specific candidates
        object_ids = []
        for cid in request.candidate_ids:
            try:
                object_ids.append(ObjectId(cid))
            except Exception:
                continue
        cursor = db["candidates"].find({"_id": {"$in": object_ids}})
    else:
        # All candidates
        cursor = db["candidates"].find({})

    candidates = []
    async for doc in cursor:
        candidates.append(doc)

    if not candidates:
        return {"job_id": request.job_id, "job_title": job["title"], "rankings": [], "total": 0}

    # Rank candidates
    job_skills = job.get("required_skills", [])
    results = []

    for candidate in candidates:
        if not candidate.get("embedding"):
            continue

        doc_score = compute_match_score(candidate["embedding"], job["embedding"])
        cv_skills = candidate.get("skills", [])
        matched, missing, skill_score = compare_skills(cv_skills, job_skills)
        
        # Final Score Logic
        final_score = skill_score
        if not job_skills and doc_score > 0:
             final_score = doc_score * 100

        results.append({
            "candidate_id": str(candidate["_id"]),
            "candidate_name": candidate["name"],
            "email": candidate.get("email", ""),
            "match_score": final_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_count": len(cv_skills),
            "language": candidate.get("language", "en"),
        })

        # Update score in DB
        await db["candidates"].update_one(
            {"_id": candidate["_id"]},
            {"$set": {"score": final_score}},
        )

    # Sort by score descending
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return {
        "job_id": request.job_id,
        "job_title": job["title"],
        "rankings": results,
        "total": len(results),
    }


@router.get("/report/{candidate_id}/{job_id}")
async def download_report(candidate_id: str, job_id: str):
    """
    Generate and download a PDF report for a candidate-job match.
    """
    db = get_database()
    candidate = await _get_candidate(db, candidate_id)
    job = await _get_job(db, job_id)

    if not candidate.get("embedding") or not job.get("embedding"):
        raise HTTPException(status_code=422, detail="Missing embeddings for report generation.")

    score = compute_match_score(candidate["embedding"], job["embedding"])
    cv_skills = candidate.get("skills", [])
    job_skills = job.get("required_skills", [])
    matched, missing, _ = compare_skills(cv_skills, job_skills)

    match_data = {
        "candidate_name": candidate["name"],
        "job_title": job["title"],
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "language": candidate.get("language", "en"),
    }

    try:
        pdf_bytes = generate_match_report(match_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

    filename = f"report_{candidate['name'].replace(' ', '_')}_{job['title'].replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get aggregate statistics for the recruiter dashboard."""
    db = get_database()

    total_candidates = await db["candidates"].count_documents({})
    total_jobs = await db["jobs"].count_documents({})

    # Average score of candidates that have been matched
    pipeline = [
        {"$match": {"score": {"$ne": None}}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}},
    ]
    avg_result = await db["candidates"].aggregate(pipeline).to_list(1)
    avg_score = round(avg_result[0]["avg_score"], 2) if avg_result else 0

    # Top candidates
    top_candidates = []
    async for doc in db["candidates"].find(
        {"score": {"$ne": None}},
        {"embedding": 0, "cleaned_text": 0, "cv_text": 0}
    ).sort("score", -1).limit(5):
        doc["id"] = str(doc.pop("_id"))
        top_candidates.append(doc)

    return {
        "total_candidates": total_candidates,
        "total_jobs": total_jobs,
        "average_score": avg_score,
        "top_candidates": top_candidates,
    }
