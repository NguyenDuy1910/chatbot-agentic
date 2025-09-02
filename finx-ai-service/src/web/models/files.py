import time
import uuid
from typing import Optional, List

from src.web.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey

class File(Base):
    __tablename__ = "file"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    hash = Column(Text)
    filename = Column(Text)
    path = Column(Text)
    data = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    access_control = Column(JSONField, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

class FileModel(BaseModel):
    id: str
    user_id: str
    hash: Optional[str] = None
    filename: str
    path: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)

class FileForm(BaseModel):
    filename: str
    hash: Optional[str] = None
    path: Optional[str] = None
    data: Optional[dict] = None
    access_control: Optional[dict] = None

class FileUpdateForm(BaseModel):
    filename: Optional[str] = None
    hash: Optional[str] = None
    path: Optional[str] = None
    data: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None

class FileResponse(BaseModel):
    id: str
    filename: str
    hash: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: int
    updated_at: int

class FilesTable:
    def insert_new_file(self, user_id: str, form_data: FileForm) -> Optional[FileModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            file = FileModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "filename": form_data.filename,
                    "hash": form_data.hash,
                    "path": form_data.path,
                    "data": form_data.data or {},
                    "meta": {},
                    "access_control": form_data.access_control or {},
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = File(**file.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return file
            else:
                return None

    def get_file_by_id(self, id: str) -> Optional[FileModel]:
        try:
            with get_db_context() as db:
                file = db.query(File).filter_by(id=id).first()
                return FileModel.model_validate(file) if file else None
        except Exception:
            return None

    def get_file_by_hash(self, hash: str) -> Optional[FileModel]:
        try:
            with get_db_context() as db:
                file = db.query(File).filter_by(hash=hash).first()
                return FileModel.model_validate(file) if file else None
        except Exception:
            return None

    def get_files_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[FileModel]:
        with get_db_context() as db:
            files = (
                db.query(File)
                .filter_by(user_id=user_id)
                .order_by(File.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [FileModel.model_validate(file) for file in files]

    def get_files_by_filename(self, filename: str, user_id: Optional[str] = None) -> List[FileModel]:
        with get_db_context() as db:
            query = db.query(File).filter_by(filename=filename)
            if user_id:
                query = query.filter_by(user_id=user_id)
            files = query.order_by(File.created_at.desc()).all()
            return [FileModel.model_validate(file) for file in files]

    def get_public_files(self) -> List[FileModel]:
        """Get files that are publicly accessible"""
        with get_db_context() as db:
            files = db.query(File).all()
            public_files = []
            for file in files:
                # Check if file is public based on access_control
                if not file.access_control or file.access_control.get("public", False):
                    public_files.append(FileModel.model_validate(file))
            return public_files

    def update_file_by_id(self, id: str, updated: dict) -> Optional[FileModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(File).filter_by(id=id).update(updated)
                db.commit()
                file = db.query(File).filter_by(id=id).first()
                return FileModel.model_validate(file) if file else None
        except Exception:
            return None

    def update_file_hash_by_id(self, id: str, hash: str) -> Optional[FileModel]:
        try:
            with get_db_context() as db:
                db.query(File).filter_by(id=id).update({
                    "hash": hash,
                    "updated_at": int(time.time())
                })
                db.commit()
                file = db.query(File).filter_by(id=id).first()
                return FileModel.model_validate(file) if file else None
        except Exception:
            return None

    def update_file_path_by_id(self, id: str, path: str) -> Optional[FileModel]:
        try:
            with get_db_context() as db:
                db.query(File).filter_by(id=id).update({
                    "path": path,
                    "updated_at": int(time.time())
                })
                db.commit()
                file = db.query(File).filter_by(id=id).first()
                return FileModel.model_validate(file) if file else None
        except Exception:
            return None

    def delete_file_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(File).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_files_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(File).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_files_by_hash(self, hash: str) -> bool:
        try:
            with get_db_context() as db:
                db.query(File).filter_by(hash=hash).delete()
                db.commit()
                return True
        except Exception:
            return False

    def get_file_count_by_user_id(self, user_id: str) -> int:
        with get_db_context() as db:
            return db.query(File).filter_by(user_id=user_id).count()

    def get_total_file_size_by_user_id(self, user_id: str) -> int:
        """Get total file size for a user (from meta data)"""
        with get_db_context() as db:
            files = db.query(File).filter_by(user_id=user_id).all()
            total_size = 0
            for file in files:
                if file.meta and "size" in file.meta:
                    total_size += file.meta.get("size", 0)
            return total_size

Files = FilesTable()
