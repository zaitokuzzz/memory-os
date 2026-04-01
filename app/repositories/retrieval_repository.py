from sqlalchemy.orm import Session

from app.models.retrieval_feedback import RetrievalFeedback
from app.models.retrieval_query import RetrievalQuery
from app.models.retrieval_result import RetrievalResult


class RetrievalRepository:
    def create_query(self, db: Session, item: RetrievalQuery) -> RetrievalQuery:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def create_result(self, db: Session, item: RetrievalResult) -> RetrievalResult:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def create_feedback(self, db: Session, item: RetrievalFeedback) -> RetrievalFeedback:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
