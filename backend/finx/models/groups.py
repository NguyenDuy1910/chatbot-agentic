import time
import uuid
from typing import Optional, List

from finx.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey

####################
# Group DB Schema
####################

class Group(Base):
    __tablename__ = "group"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, unique=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text)
    description = Column(Text)
    data = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    permissions = Column(JSONField, nullable=True)
    user_ids = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class GroupModel(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    permissions: Optional[dict] = None
    user_ids: Optional[List[str]] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class GroupForm(BaseModel):
    name: str
    description: Optional[str] = None
    user_ids: Optional[List[str]] = None


class GroupUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    permissions: Optional[dict] = None
    user_ids: Optional[List[str]] = None


####################
# Groups Table
####################

class GroupsTable:
    def insert_new_group(self, user_id: str, form_data: GroupForm) -> Optional[GroupModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            group = GroupModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": form_data.name,
                    "description": form_data.description,
                    "user_ids": form_data.user_ids or [],
                    "data": {},
                    "meta": {},
                    "permissions": {},
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Group(**group.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return group
            else:
                return None

    def get_group_by_id(self, id: str) -> Optional[GroupModel]:
        try:
            with get_db_context() as db:
                group = db.query(Group).filter_by(id=id).first()
                return GroupModel.model_validate(group) if group else None
        except Exception:
            return None

    def get_groups_by_user_id(self, user_id: str) -> List[GroupModel]:
        with get_db_context() as db:
            groups = db.query(Group).filter_by(user_id=user_id).order_by(Group.created_at.desc()).all()
            return [GroupModel.model_validate(group) for group in groups]

    def get_groups_by_member_id(self, user_id: str) -> List[GroupModel]:
        """Get groups where user is a member"""
        with get_db_context() as db:
            groups = db.query(Group).all()
            member_groups = []
            for group in groups:
                if group.user_ids and user_id in group.user_ids:
                    member_groups.append(GroupModel.model_validate(group))
            return member_groups

    def update_group_by_id(self, id: str, updated: dict) -> Optional[GroupModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Group).filter_by(id=id).update(updated)
                db.commit()
                group = db.query(Group).filter_by(id=id).first()
                return GroupModel.model_validate(group) if group else None
        except Exception:
            return None

    def add_user_to_group(self, group_id: str, user_id: str) -> Optional[GroupModel]:
        try:
            with get_db_context() as db:
                group = db.query(Group).filter_by(id=group_id).first()
                if group:
                    user_ids = group.user_ids or []
                    if user_id not in user_ids:
                        user_ids.append(user_id)
                        group.user_ids = user_ids
                        group.updated_at = int(time.time())
                        db.commit()
                    return GroupModel.model_validate(group)
                return None
        except Exception:
            return None

    def remove_user_from_group(self, group_id: str, user_id: str) -> Optional[GroupModel]:
        try:
            with get_db_context() as db:
                group = db.query(Group).filter_by(id=group_id).first()
                if group:
                    user_ids = group.user_ids or []
                    if user_id in user_ids:
                        user_ids.remove(user_id)
                        group.user_ids = user_ids
                        group.updated_at = int(time.time())
                        db.commit()
                    return GroupModel.model_validate(group)
                return None
        except Exception:
            return None

    def remove_user_from_all_groups(self, user_id: str) -> bool:
        """Remove user from all groups they belong to"""
        try:
            with get_db_context() as db:
                groups = db.query(Group).all()
                for group in groups:
                    if group.user_ids and user_id in group.user_ids:
                        user_ids = group.user_ids.copy()
                        user_ids.remove(user_id)
                        group.user_ids = user_ids
                        group.updated_at = int(time.time())
                db.commit()
                return True
        except Exception:
            return False

    def delete_group_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Group).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_groups_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Group).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False


Groups = GroupsTable()
