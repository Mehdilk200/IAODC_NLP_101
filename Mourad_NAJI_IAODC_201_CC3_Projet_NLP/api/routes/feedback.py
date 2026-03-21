"""
/api/v1/feedback — Record user feedback for personalization
"""
from fastapi import APIRouter
from api.schemas.request import FeedbackRequest
from api.schemas.response import FeedbackResponse
from services.personalization.user_profile import get_or_create_profile

router = APIRouter(tags=["Feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest):
    profile, sid = get_or_create_profile(req.session_id)
    profile.record_feedback(req.outfit_id, req.liked)
    return FeedbackResponse(
        status="ok",
        session_id=sid,
        message=f"Feedback recorded ({'👍' if req.liked else '👎'}) for outfit {req.outfit_id}",
    )
