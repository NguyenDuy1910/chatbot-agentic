import time
import uuid
from typing import Optional, List

from finx.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey

####################
# Memory DB Schema
####################

class Memory(Base):
    __tablename__ = "memory"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)


class MemoryModel(BaseModel):
    id: str
    user_id: str
    content: str
    updated_at: int
    created_at: int

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class MemoryForm(BaseModel):
    content: str


class MemoryUpdateForm(BaseModel):
    content: str


class MemoryResponse(BaseModel):
    id: str
    content: str
    created_at: int
    updated_at: int


####################
# Memories Table
####################

class MemoriesTable:
    def insert_new_memory(self, user_id: str, form_data: MemoryForm) -> Optional[MemoryModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            memory = MemoryModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "content": form_data.content,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Memory(**memory.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return memory
            else:
                return None

    def get_memory_by_id(self, id: str) -> Optional[MemoryModel]:
        try:
            with get_db_context() as db:
                memory = db.query(Memory).filter_by(id=id).first()
                return MemoryModel.model_validate(memory) if memory else None
        except Exception:
            return None

    def get_memories_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[MemoryModel]:
        with get_db_context() as db:
            memories = (
                db.query(Memory)
                .filter_by(user_id=user_id)
                .order_by(Memory.updated_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [MemoryModel.model_validate(memory) for memory in memories]

    def search_memories_by_content(self, user_id: str, search_term: str, skip: int = 0, limit: int = 50) -> List[MemoryModel]:
        """Search memories by content (case-insensitive)"""
        with get_db_context() as db:
            memories = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.content.ilike(f"%{search_term}%")
                )
                .order_by(Memory.updated_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [MemoryModel.model_validate(memory) for memory in memories]

    def get_recent_memories_by_user_id(self, user_id: str, days: int = 7, limit: int = 10) -> List[MemoryModel]:
        """Get recent memories within specified days"""
        with get_db_context() as db:
            cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
            memories = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.created_at >= cutoff_time
                )
                .order_by(Memory.created_at.desc())
                .limit(limit)
                .all()
            )
            return [MemoryModel.model_validate(memory) for memory in memories]

    def update_memory_by_id(self, id: str, updated: dict) -> Optional[MemoryModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Memory).filter_by(id=id).update(updated)
                db.commit()
                memory = db.query(Memory).filter_by(id=id).first()
                return MemoryModel.model_validate(memory) if memory else None
        except Exception:
            return None

    def update_memory_content_by_id(self, id: str, content: str) -> Optional[MemoryModel]:
        try:
            with get_db_context() as db:
                db.query(Memory).filter_by(id=id).update({
                    "content": content,
                    "updated_at": int(time.time())
                })
                db.commit()
                memory = db.query(Memory).filter_by(id=id).first()
                return MemoryModel.model_validate(memory) if memory else None
        except Exception:
            return None

    def delete_memory_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                result = db.query(Memory).filter_by(id=id).delete()
                db.commit()
                return result > 0
        except Exception:
            return False

    def delete_memories_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Memory).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def get_memory_count_by_user_id(self, user_id: str) -> int:
        with get_db_context() as db:
            return db.query(Memory).filter_by(user_id=user_id).count()

    def get_oldest_memory_by_user_id(self, user_id: str) -> Optional[MemoryModel]:
        """Get the oldest memory for a user"""
        try:
            with get_db_context() as db:
                memory = (
                    db.query(Memory)
                    .filter_by(user_id=user_id)
                    .order_by(Memory.created_at.asc())
                    .first()
                )
                return MemoryModel.model_validate(memory) if memory else None
        except Exception:
            return None

    def get_latest_memory_by_user_id(self, user_id: str) -> Optional[MemoryModel]:
        """Get the latest memory for a user"""
        try:
            with get_db_context() as db:
                memory = (
                    db.query(Memory)
                    .filter_by(user_id=user_id)
                    .order_by(Memory.created_at.desc())
                    .first()
                )
                return MemoryModel.model_validate(memory) if memory else None
        except Exception:
            return None

    def bulk_insert_memories(self, user_id: str, memory_forms: List[MemoryForm]) -> List[MemoryModel]:
        """Insert multiple memories at once"""
        with get_db_context() as db:
            created_memories = []
            for form_data in memory_forms:
                id = str(uuid.uuid4())
                memory = MemoryModel(
                    **{
                        "id": id,
                        "user_id": user_id,
                        "content": form_data.content,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time()),
                    }
                )
                result = Memory(**memory.model_dump())
                db.add(result)
                created_memories.append(memory)
            
            db.commit()
            return created_memories

    def bulk_delete_memories(self, user_id: str, memory_ids: List[str]) -> bool:
        """Delete multiple memories at once"""
        try:
            with get_db_context() as db:
                db.query(Memory).filter(
                    Memory.user_id == user_id,
                    Memory.id.in_(memory_ids)
                ).delete(synchronize_session=False)
                db.commit()
                return True
        except Exception:
            return False


Memories = MemoriesTable()
