import time
import uuid
from typing import Optional, List

from src.web.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, ForeignKey

####################
# Folder DB Schema
####################

class Folder(Base):
    __tablename__ = "folder"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    parent_id = Column(String, ForeignKey("folder.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text)
    items = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    is_expanded = Column(Boolean, default=False)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class FolderModel(BaseModel):
    id: str
    parent_id: Optional[str] = None
    user_id: str
    name: str
    items: Optional[dict] = None
    meta: Optional[dict] = None
    is_expanded: bool = False
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


####################
# Chat DB Schema
####################

class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text)
    chat = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    share_id = Column(Text, unique=True, nullable=True)
    archived = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False)
    meta = Column(JSONField, default={})
    folder_id = Column(String, ForeignKey("folder.id", ondelete="SET NULL"), nullable=True)


class ChatModel(BaseModel):
    id: str
    user_id: str
    title: str
    chat: Optional[dict] = None
    created_at: int
    updated_at: int
    share_id: Optional[str] = None
    archived: bool = False
    pinned: bool = False
    meta: Optional[dict] = {}
    folder_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class FolderForm(BaseModel):
    name: str
    parent_id: Optional[str] = None


class FolderUpdateForm(BaseModel):
    name: Optional[str] = None
    is_expanded: Optional[bool] = None
    meta: Optional[dict] = None


class ChatForm(BaseModel):
    title: str
    chat: Optional[dict] = None
    folder_id: Optional[str] = None


class ChatUpdateForm(BaseModel):
    title: Optional[str] = None
    chat: Optional[dict] = None
    archived: Optional[bool] = None
    pinned: Optional[bool] = None
    meta: Optional[dict] = None
    folder_id: Optional[str] = None


class ChatTitleForm(BaseModel):
    title: str


####################
# Folder Table
####################

class FoldersTable:
    def insert_new_folder(
        self, user_id: str, name: str, parent_id: Optional[str] = None
    ) -> Optional[FolderModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            folder = FolderModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": name,
                    "parent_id": parent_id,
                    "items": {},
                    "meta": {},
                    "is_expanded": False,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Folder(**folder.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return folder
            else:
                return None

    def get_folder_by_id(self, id: str) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id).first()
                return FolderModel.model_validate(folder) if folder else None
        except Exception:
            return None

    def get_folders_by_user_id(self, user_id: str) -> List[FolderModel]:
        with get_db_context() as db:
            folders = db.query(Folder).filter_by(user_id=user_id).order_by(Folder.created_at.desc()).all()
            return [FolderModel.model_validate(folder) for folder in folders]

    def get_folders_by_parent_id(self, parent_id: Optional[str], user_id: str) -> List[FolderModel]:
        with get_db_context() as db:
            folders = db.query(Folder).filter_by(parent_id=parent_id, user_id=user_id).order_by(Folder.created_at.desc()).all()
            return [FolderModel.model_validate(folder) for folder in folders]

    def update_folder_by_id(self, id: str, updated: dict) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Folder).filter_by(id=id).update(updated)
                db.commit()
                folder = db.query(Folder).filter_by(id=id).first()
                return FolderModel.model_validate(folder) if folder else None
        except Exception:
            return None

    def delete_folder_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                # Delete all subfolders recursively
                self._delete_subfolders_recursive(db, id)
                # Delete the folder itself
                db.query(Folder).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def _delete_subfolders_recursive(self, db, parent_id: str):
        """Recursively delete all subfolders"""
        subfolders = db.query(Folder).filter_by(parent_id=parent_id).all()
        for subfolder in subfolders:
            self._delete_subfolders_recursive(db, subfolder.id)
            db.query(Folder).filter_by(id=subfolder.id).delete()


####################
# Chat Table
####################

class ChatsTable:
    def insert_new_chat(self, user_id: str, form_data: ChatForm) -> Optional[ChatModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            chat = ChatModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "title": form_data.title,
                    "chat": form_data.chat,
                    "folder_id": form_data.folder_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Chat(**chat.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return chat
            else:
                return None

    def get_chat_by_id(self, id: str) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                chat = db.query(Chat).filter_by(id=id).first()
                return ChatModel.model_validate(chat) if chat else None
        except Exception:
            return None

    def get_chat_by_share_id(self, share_id: str) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                chat = db.query(Chat).filter_by(share_id=share_id).first()
                return ChatModel.model_validate(chat) if chat else None
        except Exception:
            return None

    def get_chats_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[ChatModel]:
        with get_db_context() as db:
            chats = (
                db.query(Chat)
                .filter_by(user_id=user_id)
                .order_by(Chat.updated_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [ChatModel.model_validate(chat) for chat in chats]

    def get_chats_by_folder_id(self, folder_id: Optional[str], user_id: str) -> List[ChatModel]:
        with get_db_context() as db:
            chats = (
                db.query(Chat)
                .filter_by(folder_id=folder_id, user_id=user_id)
                .order_by(Chat.updated_at.desc())
                .all()
            )
            return [ChatModel.model_validate(chat) for chat in chats]

    def get_archived_chats_by_user_id(self, user_id: str) -> List[ChatModel]:
        with get_db_context() as db:
            chats = (
                db.query(Chat)
                .filter_by(user_id=user_id, archived=True)
                .order_by(Chat.updated_at.desc())
                .all()
            )
            return [ChatModel.model_validate(chat) for chat in chats]

    def get_pinned_chats_by_user_id(self, user_id: str) -> List[ChatModel]:
        with get_db_context() as db:
            chats = (
                db.query(Chat)
                .filter_by(user_id=user_id, pinned=True)
                .order_by(Chat.updated_at.desc())
                .all()
            )
            return [ChatModel.model_validate(chat) for chat in chats]

    def update_chat_by_id(self, id: str, updated: dict) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Chat).filter_by(id=id).update(updated)
                db.commit()
                chat = db.query(Chat).filter_by(id=id).first()
                return ChatModel.model_validate(chat) if chat else None
        except Exception:
            return None

    def update_chat_share_id_by_id(self, id: str, share_id: Optional[str]) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(id=id).update({
                    "share_id": share_id,
                    "updated_at": int(time.time())
                })
                db.commit()
                chat = db.query(Chat).filter_by(id=id).first()
                return ChatModel.model_validate(chat) if chat else None
        except Exception:
            return None

    def toggle_chat_archive_by_id(self, id: str) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                chat = db.query(Chat).filter_by(id=id).first()
                if chat:
                    chat.archived = not chat.archived
                    chat.updated_at = int(time.time())
                    db.commit()
                    return ChatModel.model_validate(chat)
                return None
        except Exception:
            return None

    def toggle_chat_pin_by_id(self, id: str) -> Optional[ChatModel]:
        try:
            with get_db_context() as db:
                chat = db.query(Chat).filter_by(id=id).first()
                if chat:
                    chat.pinned = not chat.pinned
                    chat.updated_at = int(time.time())
                    db.commit()
                    return ChatModel.model_validate(chat)
                return None
        except Exception:
            return None

    def delete_chat_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_chats_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False


Folders = FoldersTable()
Chats = ChatsTable()