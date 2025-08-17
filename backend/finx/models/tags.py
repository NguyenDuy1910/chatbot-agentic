from typing import Optional, List

from finx.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, ForeignKey

####################
# Tag DB Schema
####################

class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meta = Column(JSONField, nullable=True)


class TagModel(BaseModel):
    id: str
    name: str
    user_id: str
    meta: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class TagForm(BaseModel):
    id: str
    name: str
    meta: Optional[dict] = None


class TagUpdateForm(BaseModel):
    name: Optional[str] = None
    meta: Optional[dict] = None


class TagResponse(BaseModel):
    id: str
    name: str
    meta: Optional[dict] = None


####################
# Tags Table
####################

class TagsTable:
    def insert_new_tag(self, user_id: str, form_data: TagForm) -> Optional[TagModel]:
        with get_db_context() as db:
            # Check if tag already exists for this user
            existing_tag = db.query(Tag).filter_by(id=form_data.id, user_id=user_id).first()
            if existing_tag:
                return None
            
            tag = TagModel(
                **{
                    "id": form_data.id,
                    "name": form_data.name,
                    "user_id": user_id,
                    "meta": form_data.meta or {},
                }
            )
            result = Tag(**tag.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return tag
            else:
                return None

    def get_tag_by_id_and_user_id(self, id: str, user_id: str) -> Optional[TagModel]:
        try:
            with get_db_context() as db:
                tag = db.query(Tag).filter_by(id=id, user_id=user_id).first()
                return TagModel.model_validate(tag) if tag else None
        except Exception:
            return None

    def get_tags_by_user_id(self, user_id: str) -> List[TagModel]:
        with get_db_context() as db:
            tags = db.query(Tag).filter_by(user_id=user_id).order_by(Tag.name.asc()).all()
            return [TagModel.model_validate(tag) for tag in tags]

    def get_tags_by_name(self, name: str, user_id: str) -> List[TagModel]:
        with get_db_context() as db:
            tags = db.query(Tag).filter_by(name=name, user_id=user_id).all()
            return [TagModel.model_validate(tag) for tag in tags]

    def search_tags_by_name(self, name_pattern: str, user_id: str) -> List[TagModel]:
        """Search tags by name pattern (case-insensitive)"""
        with get_db_context() as db:
            tags = db.query(Tag).filter(
                Tag.user_id == user_id,
                Tag.name.ilike(f"%{name_pattern}%")
            ).order_by(Tag.name.asc()).all()
            return [TagModel.model_validate(tag) for tag in tags]

    def update_tag_by_id_and_user_id(self, id: str, user_id: str, updated: dict) -> Optional[TagModel]:
        try:
            with get_db_context() as db:
                db.query(Tag).filter_by(id=id, user_id=user_id).update(updated)
                db.commit()
                tag = db.query(Tag).filter_by(id=id, user_id=user_id).first()
                return TagModel.model_validate(tag) if tag else None
        except Exception:
            return None

    def delete_tag_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                result = db.query(Tag).filter_by(id=id, user_id=user_id).delete()
                db.commit()
                return result > 0
        except Exception:
            return False

    def delete_tags_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Tag).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def get_tag_count_by_user_id(self, user_id: str) -> int:
        with get_db_context() as db:
            return db.query(Tag).filter_by(user_id=user_id).count()

    def get_unique_tag_names_by_user_id(self, user_id: str) -> List[str]:
        """Get unique tag names for a user"""
        with get_db_context() as db:
            tags = db.query(Tag.name).filter_by(user_id=user_id).distinct().all()
            return [tag.name for tag in tags]

    def bulk_insert_tags(self, user_id: str, tag_forms: List[TagForm]) -> List[TagModel]:
        """Insert multiple tags at once"""
        with get_db_context() as db:
            created_tags = []
            for form_data in tag_forms:
                # Check if tag already exists
                existing_tag = db.query(Tag).filter_by(id=form_data.id, user_id=user_id).first()
                if not existing_tag:
                    tag = TagModel(
                        **{
                            "id": form_data.id,
                            "name": form_data.name,
                            "user_id": user_id,
                            "meta": form_data.meta or {},
                        }
                    )
                    result = Tag(**tag.model_dump())
                    db.add(result)
                    created_tags.append(tag)
            
            db.commit()
            return created_tags

    def bulk_delete_tags(self, user_id: str, tag_ids: List[str]) -> bool:
        """Delete multiple tags at once"""
        try:
            with get_db_context() as db:
                db.query(Tag).filter(
                    Tag.user_id == user_id,
                    Tag.id.in_(tag_ids)
                ).delete(synchronize_session=False)
                db.commit()
                return True
        except Exception:
            return False


Tags = TagsTable()
