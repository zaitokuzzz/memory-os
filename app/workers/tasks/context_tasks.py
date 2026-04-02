from app.db.session import SessionLocal
from app.models.context_bundle import ContextBundle
from app.repositories.context_bundle_repository import ContextBundleRepository
from app.repositories.memory_repository import MemoryRepository
from app.services.job_tracking_service import JobTrackingService
from app.services.summarizer_service import SummarizerService
from app.utils.text import make_bundle_key
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
bundle_repo = ContextBundleRepository()
summarizer = SummarizerService()
job_tracker = JobTrackingService()


@celery_app.task(name="update_context_bundle")
def update_context_bundle_task(memory_id: str) -> dict:
    job_id = job_tracker.create_job("update_context_bundle", {"memory_id": memory_id})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        memory = memory_repo.get_by_id(db, memory_id)
        if not memory:
            job_tracker.mark_failed(job_id, "memory_not_found")
            return {"status": "not_found", "memory_id": memory_id}

        base_text = memory.summary or memory.content
        bundle_key = make_bundle_key(base_text)

        related = memory_repo.search_by_type_basic(
            db=db,
            owner_id=memory.owner_id,
            agent_id=memory.agent_id,
            memory_type="episodic",
            query=base_text[:60],
            limit=20,
        )

        if not related:
            related = [memory]

        summaries = [m.summary or m.content[:200] for m in related]
        topic_tags = summarizer.extract_topics(summaries)
        bundle_summary = summarizer.generate_daily_summary(summaries)

        existing = bundle_repo.get_by_key(db, memory.owner_id, memory.agent_id, bundle_key)

        memory_ids = [str(m.id) for m in related]
        start_time = min(m.timestamp_at for m in related)
        end_time = max(m.timestamp_at for m in related)

        if existing:
            existing.summary = bundle_summary
            existing.topic_tags = topic_tags
            existing.memory_ids = memory_ids
            existing.start_time = start_time
            existing.end_time = end_time
            bundle_repo.update(db, existing)
            job_tracker.mark_success(job_id)
            return {"status": "ok", "bundle_id": str(existing.id), "updated": True, "job_id": job_id}

        item = ContextBundle(
            owner_id=memory.owner_id,
            agent_id=memory.agent_id,
            bundle_key=bundle_key,
            title=bundle_key,
            summary=bundle_summary,
            topic_tags=topic_tags,
            memory_ids=memory_ids,
            start_time=start_time,
            end_time=end_time,
        )
        created = bundle_repo.create(db, item)
        job_tracker.mark_success(job_id)
        return {"status": "ok", "bundle_id": str(created.id), "created": True, "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
