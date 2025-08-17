import time
import uuid
from typing import Optional, List

from finx.internal.db import Base, JSONField, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey

####################
# Feedback DB Schema
####################

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    version = Column(BigInteger, default=0)
    type = Column(Text)
    data = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    snapshot = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class FeedbackModel(BaseModel):
    id: str
    user_id: str
    version: int = 0
    type: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    snapshot: Optional[dict] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class FeedbackForm(BaseModel):
    type: str
    data: Optional[dict] = None
    snapshot: Optional[dict] = None


class FeedbackUpdateForm(BaseModel):
    type: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    snapshot: Optional[dict] = None
    version: Optional[int] = None


class FeedbackResponse(BaseModel):
    id: str
    type: Optional[str] = None
    version: int
    created_at: int
    updated_at: int


####################
# Feedback Table
####################

class FeedbackTable:
    def insert_new_feedback(self, user_id: str, form_data: FeedbackForm) -> Optional[FeedbackModel]:
        with get_db() as db:
            id = str(uuid.uuid4())
            feedback = FeedbackModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "type": form_data.type,
                    "data": form_data.data or {},
                    "snapshot": form_data.snapshot or {},
                    "meta": {},
                    "version": 0,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Feedback(**feedback.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return feedback
            else:
                return None

    def get_feedback_by_id(self, id: str) -> Optional[FeedbackModel]:
        try:
            with get_db() as db:
                feedback = db.query(Feedback).filter_by(id=id).first()
                return FeedbackModel.model_validate(feedback) if feedback else None
        except Exception:
            return None

    def get_feedback_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[FeedbackModel]:
        with get_db() as db:
            feedback_list = (
                db.query(Feedback)
                .filter_by(user_id=user_id)
                .order_by(Feedback.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [FeedbackModel.model_validate(feedback) for feedback in feedback_list]

    def get_feedback_by_type(self, type: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[FeedbackModel]:
        with get_db() as db:
            query = db.query(Feedback).filter_by(type=type)
            if user_id:
                query = query.filter_by(user_id=user_id)
            feedback_list = (
                query
                .order_by(Feedback.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [FeedbackModel.model_validate(feedback) for feedback in feedback_list]

    def get_recent_feedback(self, days: int = 7, limit: int = 50) -> List[FeedbackModel]:
        """Get recent feedback within specified days"""
        with get_db() as db:
            cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
            feedback_list = (
                db.query(Feedback)
                .filter(Feedback.created_at >= cutoff_time)
                .order_by(Feedback.created_at.desc())
                .limit(limit)
                .all()
            )
            return [FeedbackModel.model_validate(feedback) for feedback in feedback_list]

    def get_feedback_by_version(self, version: int, user_id: Optional[str] = None) -> List[FeedbackModel]:
        with get_db() as db:
            query = db.query(Feedback).filter_by(version=version)
            if user_id:
                query = query.filter_by(user_id=user_id)
            feedback_list = query.order_by(Feedback.created_at.desc()).all()
            return [FeedbackModel.model_validate(feedback) for feedback in feedback_list]

    def update_feedback_by_id(self, id: str, updated: dict) -> Optional[FeedbackModel]:
        try:
            with get_db() as db:
                updated["updated_at"] = int(time.time())
                db.query(Feedback).filter_by(id=id).update(updated)
                db.commit()
                feedback = db.query(Feedback).filter_by(id=id).first()
                return FeedbackModel.model_validate(feedback) if feedback else None
        except Exception:
            return None

    def increment_feedback_version_by_id(self, id: str) -> Optional[FeedbackModel]:
        try:
            with get_db() as db:
                feedback = db.query(Feedback).filter_by(id=id).first()
                if feedback:
                    feedback.version += 1
                    feedback.updated_at = int(time.time())
                    db.commit()
                    return FeedbackModel.model_validate(feedback)
                return None
        except Exception:
            return None

    def delete_feedback_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                result = db.query(Feedback).filter_by(id=id).delete()
                db.commit()
                return result > 0
        except Exception:
            return False

    def delete_feedback_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db() as db:
                db.query(Feedback).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_feedback_by_type(self, type: str, user_id: Optional[str] = None) -> bool:
        try:
            with get_db() as db:
                query = db.query(Feedback).filter_by(type=type)
                if user_id:
                    query = query.filter_by(user_id=user_id)
                query.delete()
                db.commit()
                return True
        except Exception:
            return False

    def get_feedback_count_by_user_id(self, user_id: str) -> int:
        with get_db() as db:
            return db.query(Feedback).filter_by(user_id=user_id).count()

    def get_feedback_count_by_type(self, type: str) -> int:
        with get_db() as db:
            return db.query(Feedback).filter_by(type=type).count()

    def get_feedback_types_by_user_id(self, user_id: str) -> List[str]:
        """Get unique feedback types for a user"""
        with get_db() as db:
            types = db.query(Feedback.type).filter_by(user_id=user_id).distinct().all()
            return [type_row.type for type_row in types if type_row.type]

    def get_all_feedback_types(self) -> List[str]:
        """Get all unique feedback types"""
        with get_db() as db:
            types = db.query(Feedback.type).distinct().all()
            return [type_row.type for type_row in types if type_row.type]

    def bulk_delete_feedback(self, user_id: str, feedback_ids: List[str]) -> bool:
        """Delete multiple feedback entries at once"""
        try:
            with get_db() as db:
                db.query(Feedback).filter(
                    Feedback.user_id == user_id,
                    Feedback.id.in_(feedback_ids)
                ).delete(synchronize_session=False)
                db.commit()
                return True
        except Exception:
            return False


Feedbacks = FeedbackTable()
