from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.semantic_cluster import SemanticCluster


class SemanticClusterRepository:
    def get_by_key(self, db: Session, owner_id, agent_id, cluster_key: str):
        stmt = (
            select(SemanticCluster)
            .where(SemanticCluster.owner_id == owner_id)
            .where(SemanticCluster.cluster_key == cluster_key)
        )

        if agent_id:
            stmt = stmt.where(SemanticCluster.agent_id == agent_id)

        return db.scalar(stmt)

    def create(self, db: Session, item: SemanticCluster) -> SemanticCluster:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, item: SemanticCluster) -> SemanticCluster:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
