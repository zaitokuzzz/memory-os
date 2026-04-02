from datetime import datetime, timezone

from app.services.scoring_service import ScoringService


def test_compute_decay():
    service = ScoringService()
    score = service.compute_decay("episodic", datetime.now(timezone.utc))
    assert score > 0


def test_compute_final_score():
    service = ScoringService()
    score = service.compute_final_score(
        relevance=0.8,
        importance=0.9,
        confidence=0.9,
        decay=1.0,
        source_weight=1.0,
    )
    assert score > 0
