"""KathaYantra Data Repositories Package."""

from app.repositories.candidate_repository import CandidateRepository, candidate_repository
from app.repositories.story_repository import StoryRepository, story_repository

__all__ = [
    "CandidateRepository",
    "candidate_repository",
    "StoryRepository",
    "story_repository",
]



