"""
User Profile — Session-based Personalization
Accumulates user preferences across a conversation session.
In-memory; can be backed by Redis or DB for multi-session persistence.
"""
from __future__ import annotations
import uuid
import time
from collections import Counter
from threading import Lock
from services.nlp.preference_extractor import PreferenceResult

_profiles: dict[str, "UserProfile"] = {}
_lock = Lock()


class UserProfile:
    """Tracks a single user's expressed preferences in a session."""

    def __init__(self, session_id: str):
        self.session_id   = session_id
        self.created_at   = time.time()
        self.last_active  = time.time()
        self.history: list[dict] = []          # list of PreferenceResult.to_dict()
        self.liked_outfit_ids: set[str] = set()
        self.disliked_outfit_ids: set[str] = set()
        self._slot_counter: Counter = Counter()

    def record_query(self, prefs: PreferenceResult) -> None:
        self.last_active = time.time()
        self.history.append(prefs.to_dict())
        # Track slot frequencies for preference learning
        for slot in ["gender", "occasion", "season", "style", "color"]:
            val = getattr(prefs, slot, None)
            if val:
                self._slot_counter[f"{slot}:{val}"] += 1

    def record_feedback(self, outfit_id: str, liked: bool) -> None:
        if liked:
            self.liked_outfit_ids.add(outfit_id)
            self.disliked_outfit_ids.discard(outfit_id)
        else:
            self.disliked_outfit_ids.add(outfit_id)
            self.liked_outfit_ids.discard(outfit_id)

    def get_preferred_style(self) -> str | None:
        style_counts = {
            k.split(":")[1]: v
            for k, v in self._slot_counter.items()
            if k.startswith("style:")
        }
        return max(style_counts, key=style_counts.get) if style_counts else None

    def get_preferred_gender(self) -> str | None:
        gender_counts = {
            k.split(":")[1]: v
            for k, v in self._slot_counter.items()
            if k.startswith("gender:")
        }
        return max(gender_counts, key=gender_counts.get) if gender_counts else None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "history_count": len(self.history),
            "preferred_style": self.get_preferred_style(),
            "preferred_gender": self.get_preferred_gender(),
            "liked_outfits": list(self.liked_outfit_ids),
        }


def get_or_create_profile(session_id: str | None) -> tuple[UserProfile, str]:
    """Get an existing profile or create a new one. Returns (profile, session_id)."""
    sid = session_id or str(uuid.uuid4())
    with _lock:
        if sid not in _profiles:
            _profiles[sid] = UserProfile(sid)
        return _profiles[sid], sid


def get_profile(session_id: str) -> UserProfile | None:
    return _profiles.get(session_id)
