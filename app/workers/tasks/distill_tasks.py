from datetime import datetime, timezone

from app.core.enums import MemoryStatus, MemoryType
from app.db.session import SessionLocal
from app.models.memory_item import MemoryItem
from app.models.semantic_cluster import SemanticCluster
from app.repositories.memory_repository import MemoryRepository
from app.repositories.semantic_cluster_repository import SemanticClusterRepository
from app.services.job_tracking_service import JobTrackingService
from app.services.summarizer_service import SummarizerService
from app.utils.text import make_bundle_key
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
summarizer = SummarizerService()
cluster_repo = SemanticClusterRepository()
job_tracker = JobTrackingService()

DISTILL_MIN_CLUSTER_SIZE = 3


@celery_app.task(name="distill_candidate_check")
def distill_candidate_check_task(memory_id: str) -> dict:
    job_id = job_tracker.create_job("distill_candidate_check", {"memory_id": memory_id})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        memory = memory_repo.get_by_id(db, memory_id)
        if not memory:
            job_tracker.mark_failed(job_id, "memory_not_found")
            return {"status": "not_found", "memory_id": memory_id}

        similar = memory_repo.search_by_type_basic(
            db=db,
            owner_id=memory.owner_id,
            agent_id=memory.agent_id,
            memory_type="episodic",
            query=(memory.summary or memory.content)[:80],
            limit=10,
        )

        if len(similar) >= DISTILL_MIN_CLUSTER_SIZE:
            run_distillation_task.delay([str(m.id) for m in similar])
            job_tracker.mark_success(job_id)
            return {"status": "queued_for_distillation", "count": len(similar), "job_id": job_id}

        memory.status = MemoryStatus.PENDING_DISTILL
        memory_repo.update(db, memory)
        job_tracker.mark_success(job_id)
        return {"status": "pending_distill", "count": len(similar), "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()


@celery_app.task(name="run_distillation")
def run_distillation_task(memory_ids: list[str]) -> dict:
    job_id = job_tracker.create_job("run_distillation", {"memory_ids": memory_ids})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        sources = []
        for memory_id in memory_ids:
            item = memory_repo.get_by_id(db, memory_id)
            if item and item.memory_type == MemoryType.EPISODIC:
                sources.append(item)

        if len(sources) < DISTILL_MIN_CLUSTER_SIZE:
            job_tracker.mark_success(job_id)
            return {"status": "skipped", "reason": "not_enough_sources", "job_id": job_id}

        source_summaries = [m.summary or m.content[:200] for m in sources]
        semantic_summary = summarizer.generate_daily_summary(source_summaries)
        cluster_key = make_bundle_key(" ".join(source_summaries)[:200])

        existing_cluster = cluster_repo.get_by_key(
            db, sources[0].owner_id, sources[0].agent_id, cluster_key
        )

        if existing_cluster:
            existing_cluster.memory_ids = [str(m.id) for m in sources]
            existing_cluster.cluster_size = len(sources)
            existing_cluster.confidence_score = 0.85
            cluster_repo.update(db, existing_cluster)
        else:
            cluster_item = SemanticCluster(
                owner_id=sources[0].owner_id,
                agent_id=sources[0].agent_id,
                cluster_key=cluster_key,
                memory_ids=[str(m.id) for m in sources],
                confidence_score=0.85,
                cluster_size=len(sources),
            )
            cluster_repo.create(db, cluster_item)

        semantic_memory = MemoryItem(
            owner_id=sources[0].owner_id,
            agent_id=sources[0].agent_id,
            memory_type=MemoryType.SEMANTIC,
            subtype="distilled_topic",
            title="Distilled semantic memory",
            content=semantic_summary,
            summary=semantic_summary,
            timestamp_at=datetime.now(timezone.utc),
            importance_score=0.85,
            confidence_score=0.85,
            source_weight=0.9,
            status=MemoryStatus.PENDING_EMBEDDING,
            metadata_json={
                "source_ids": [str(m.id) for m in sources],
                "distilled_from": "episodic_cluster",
            },
        )

        created = memory_repo.create(db, semantic_memory)

        for source in sources:
            source.importance_score = max(0.1, source.importance_score * 0.9)
            memory_repo.update(db, source)

        from app.workers.tasks.embedding_tasks import generate_embedding_task
        generate_embedding_task.delay(str(created.id))

        job_tracker.mark_success(job_id)
        return {"status": "ok", "semantic_memory_id": str(created.id), "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
