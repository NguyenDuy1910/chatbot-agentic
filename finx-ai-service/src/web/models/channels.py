import time
import uuid
from typing import Optional, List

from src.web.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey


class Channel(Base):
    __tablename__ = "channel"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text)
    name = Column(Text)
    description = Column(Text)
    data = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    access_control = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class ChannelModel(BaseModel):
    id: str
    user_id: str
    type: Optional[str] = None
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class ChannelForm(BaseModel):
    name: str
    type: Optional[str] = "general"
    description: Optional[str] = None
    access_control: Optional[dict] = None


class ChannelUpdateForm(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None

class ChannelsTable:
    def insert_new_channel(self, user_id: str, form_data: ChannelForm) -> Optional[ChannelModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            channel = ChannelModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": form_data.name,
                    "type": form_data.type,
                    "description": form_data.description,
                    "access_control": form_data.access_control or {},
                    "data": {},
                    "meta": {},
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Channel(**channel.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return channel
            else:
                return None

    def get_channel_by_id(self, id: str) -> Optional[ChannelModel]:
        try:
            with get_db_context() as db:
                channel = db.query(Channel).filter_by(id=id).first()
                return ChannelModel.model_validate(channel) if channel else None
        except Exception:
            return None

    def get_channels_by_user_id(self, user_id: str) -> List[ChannelModel]:
        with get_db_context() as db:
            channels = db.query(Channel).filter_by(user_id=user_id).order_by(Channel.created_at.desc()).all()
            return [ChannelModel.model_validate(channel) for channel in channels]

    def get_channels_by_type(self, type: str, user_id: Optional[str] = None) -> List[ChannelModel]:
        with get_db_context() as db:
            query = db.query(Channel).filter_by(type=type)
            if user_id:
                query = query.filter_by(user_id=user_id)
            channels = query.order_by(Channel.created_at.desc()).all()
            return [ChannelModel.model_validate(channel) for channel in channels]

    def get_public_channels(self) -> List[ChannelModel]:
        """Get channels that are publicly accessible"""
        with get_db_context() as db:
            channels = db.query(Channel).all()
            public_channels = []
            for channel in channels:
                # Check if channel is public based on access_control
                if not channel.access_control or channel.access_control.get("public", False):
                    public_channels.append(ChannelModel.model_validate(channel))
            return public_channels

    def update_channel_by_id(self, id: str, updated: dict) -> Optional[ChannelModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Channel).filter_by(id=id).update(updated)
                db.commit()
                channel = db.query(Channel).filter_by(id=id).first()
                return ChannelModel.model_validate(channel) if channel else None
        except Exception:
            return None

    def delete_channel_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Channel).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_channels_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Channel).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False


Channels = ChannelsTable()
