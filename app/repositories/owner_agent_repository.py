from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.owner import Owner


class OwnerAgentRepository:
    def get_owner(self, db: Session, owner_id):
        stmt = select(Owner).where(Owner.id == owner_id)
        return db.scalar(stmt)

    def get_agent(self, db: Session, agent_id):
        stmt = select(Agent).where(Agent.id == agent_id)
        return db.scalar(stmt)
