from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.owner_agent_repository import OwnerAgentRepository

repo = OwnerAgentRepository()


def validate_owner_agent(db: Session, owner_id, agent_id=None):
    owner = repo.get_owner(db, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    if agent_id:
        agent = repo.get_agent(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if str(agent.owner_id) != str(owner_id):
            raise HTTPException(status_code=400, detail="Agent does not belong to owner")
