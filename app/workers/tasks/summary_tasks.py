from datetime import date

from app.db.session import SessionLocal
from app.repositories.memory_repository import MemoryRepository
from app.services.job_tracking_service import JobTrackingService
from app.services.summarizer_service import SummarizerService
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
summarizer = SummarizerService()
job_tracker = JobTrackingService()


@celery_app.task(name="update_daily_summary")
def update_daily_summary_task(owner_id: str, agent_id: str | None, target_date: str) -> dict:
    job_id = job_tracker.create_job("update_daily_summary", {"owner_id": owner_id, "target_date": target_date})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        parsed_date = date.fromisoformat(target_date)

        memories = memory_repo.list_recent_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="episodic",
            limit=100,
        )

        day_memories = [m for m in memories if m.timestamp_at.date() == parsed_date]

        if not day_memories:
            job_tracker.mark_success(job_id)
            return {"status": "empty", "date": target_date, "job_id": job_id}

        memory_summaries = [m.summary or m.content[:200] for m in day_memories]
        summary = summarizer.generate_daily_summary(memory_summaries)
        topics = summarizer.extract_topics(memory_summaries)
        behavior_signal = summarizer.extract_behavior_signal(memory_summaries)

        item = memory_repo.upsert_daily_summary(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            summary_date=parsed_date,
            summary=summary,
            topics=topics,
            behavior_signal=behavior_signal,
            memory_ids=[str(m.id) for m in day_memories],
        )

        job_tracker.mark_success(job_id)
        return {"status": "ok", "daily_summary_id": str(item.id), "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
