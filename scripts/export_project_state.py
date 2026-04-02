import json
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.browser_source import BrowserSource
from app.models.context_bundle import ContextBundle
from app.models.daily_summary import DailySummary
from app.models.memory_archive import MemoryArchive
from app.models.memory_embedding import MemoryEmbedding
from app.models.memory_item import MemoryItem
from app.models.retrieval_feedback import RetrievalFeedback
from app.models.retrieval_query import RetrievalQuery
from app.models.retrieval_result import RetrievalResult
from app.models.semantic_cluster import SemanticCluster
from app.models.worker_job import WorkerJob


def serialize_rows(rows):
    output = []
    for row in rows:
        data = {}
        for column in row.__table__.columns:
            value = getattr(row, column.name)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            elif hasattr(value, "value"):
                value = value.value
            elif value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                value = str(value)
            data[column.name] = value
        output.append(data)
    return output


def main():
    db = SessionLocal()
    try:
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        payload = {
            "memory_items": serialize_rows(db.scalars(select(MemoryItem)).all()),
            "memory_embeddings": serialize_rows(db.scalars(select(MemoryEmbedding)).all()),
            "daily_summaries": serialize_rows(db.scalars(select(DailySummary)).all()),
            "context_bundles": serialize_rows(db.scalars(select(ContextBundle)).all()),
            "retrieval_queries": serialize_rows(db.scalars(select(RetrievalQuery)).all()),
            "retrieval_results": serialize_rows(db.scalars(select(RetrievalResult)).all()),
            "retrieval_feedback": serialize_rows(db.scalars(select(RetrievalFeedback)).all()),
            "browser_sources": serialize_rows(db.scalars(select(BrowserSource)).all()),
            "semantic_clusters": serialize_rows(db.scalars(select(SemanticCluster)).all()),
            "memory_archives": serialize_rows(db.scalars(select(MemoryArchive)).all()),
            "worker_jobs": serialize_rows(db.scalars(select(WorkerJob)).all()),
        }

        out_file = export_dir / "project_state.json"
        out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Exported project state to {out_file}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
