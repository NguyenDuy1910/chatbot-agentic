import time
import uuid
from typing import Optional, List

from src.web.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey


class Message(Base):
    __tablename__ = "message"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String, ForeignKey("channel.id", ondelete="CASCADE"), nullable=True)
    parent_id = Column(String, ForeignKey("message.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text)
    data = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class MessageModel(BaseModel):
    id: str
    user_id: str
    channel_id: Optional[str] = None
    parent_id: Optional[str] = None
    content: str
    data: Optional[dict] = None
    meta: Optional[dict] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class MessageReaction(Base):
    __tablename__ = "message_reaction"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String, ForeignKey("message.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text)
    created_at = Column(BigInteger)


class MessageReactionModel(BaseModel):
    id: str
    user_id: str
    message_id: str
    name: str
    created_at: int

    model_config = ConfigDict(from_attributes=True)


class MessageForm(BaseModel):
    content: str
    channel_id: Optional[str] = None
    parent_id: Optional[str] = None
    data: Optional[dict] = None


class MessageUpdateForm(BaseModel):
    content: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None


class MessageReactionForm(BaseModel):
    name: str


####################
class MessagesTable:
    def insert_new_message(self, user_id: str, form_data: MessageForm) -> Optional[MessageModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            message = MessageModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "channel_id": form_data.channel_id,
                    "parent_id": form_data.parent_id,
                    "content": form_data.content,
                    "data": form_data.data or {},
                    "meta": {},
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Message(**message.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return message
            else:
                return None

    def get_message_by_id(self, id: str) -> Optional[MessageModel]:
        try:
            with get_db_context() as db:
                message = db.query(Message).filter_by(id=id).first()
                return MessageModel.model_validate(message) if message else None
        except Exception:
            return None

    def get_messages_by_channel_id(self, channel_id: str, skip: int = 0, limit: int = 50) -> List[MessageModel]:
        with get_db_context() as db:
            messages = (
                db.query(Message)
                .filter_by(channel_id=channel_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [MessageModel.model_validate(message) for message in messages]

    def get_messages_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[MessageModel]:
        with get_db_context() as db:
            messages = (
                db.query(Message)
                .filter_by(user_id=user_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [MessageModel.model_validate(message) for message in messages]

    def get_replies_by_parent_id(self, parent_id: str) -> List[MessageModel]:
        with get_db_context() as db:
            messages = (
                db.query(Message)
                .filter_by(parent_id=parent_id)
                .order_by(Message.created_at.asc())
                .all()
            )
            return [MessageModel.model_validate(message) for message in messages]

    def update_message_by_id(self, id: str, updated: dict) -> Optional[MessageModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Message).filter_by(id=id).update(updated)
                db.commit()
                message = db.query(Message).filter_by(id=id).first()
                return MessageModel.model_validate(message) if message else None
        except Exception:
            return None

    def delete_message_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                # Delete all replies first
                db.query(Message).filter_by(parent_id=id).delete()
                # Delete the message itself
                db.query(Message).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_messages_by_channel_id(self, channel_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Message).filter_by(channel_id=channel_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_messages_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Message).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False


class MessageReactionsTable:
    def insert_new_reaction(self, user_id: str, message_id: str, form_data: MessageReactionForm) -> Optional[MessageReactionModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            reaction = MessageReactionModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "message_id": message_id,
                    "name": form_data.name,
                    "created_at": int(time.time()),
                }
            )
            result = MessageReaction(**reaction.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return reaction
            else:
                return None

    def get_reactions_by_message_id(self, message_id: str) -> List[MessageReactionModel]:
        with get_db_context() as db:
            reactions = db.query(MessageReaction).filter_by(message_id=message_id).order_by(MessageReaction.created_at.asc()).all()
            return [MessageReactionModel.model_validate(reaction) for reaction in reactions]

    def get_reaction_by_user_and_message(self, user_id: str, message_id: str, name: str) -> Optional[MessageReactionModel]:
        try:
            with get_db_context() as db:
                reaction = db.query(MessageReaction).filter_by(user_id=user_id, message_id=message_id, name=name).first()
                return MessageReactionModel.model_validate(reaction) if reaction else None
        except Exception:
            return None

    def delete_reaction_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(MessageReaction).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_reaction_by_user_and_message(self, user_id: str, message_id: str, name: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(MessageReaction).filter_by(user_id=user_id, message_id=message_id, name=name).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_reactions_by_message_id(self, message_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(MessageReaction).filter_by(message_id=message_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_reactions_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(MessageReaction).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False


Messages = MessagesTable()
MessageReactions = MessageReactionsTable()
