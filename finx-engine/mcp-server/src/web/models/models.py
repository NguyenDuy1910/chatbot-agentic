import time
import uuid
from typing import Optional, List

from src.web.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, ForeignKey

class Model(Base):
    __tablename__ = "model"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    base_model_id = Column(String, ForeignKey("model.id", ondelete="SET NULL"), nullable=True)
    name = Column(Text)
    params = Column(JSONField, nullable=True)
    meta = Column(JSONField, nullable=True)
    access_control = Column(JSONField, nullable=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)

class ModelModel(BaseModel):
    id: str
    user_id: str
    base_model_id: Optional[str] = None
    name: str
    params: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    is_active: bool = True
    updated_at: int
    created_at: int

    model_config = ConfigDict(from_attributes=True)

class ModelForm(BaseModel):
    name: str
    base_model_id: Optional[str] = None
    params: Optional[dict] = None
    access_control: Optional[dict] = None

class ModelUpdateForm(BaseModel):
    name: Optional[str] = None
    base_model_id: Optional[str] = None
    params: Optional[dict] = None
    meta: Optional[dict] = None
    access_control: Optional[dict] = None
    is_active: Optional[bool] = None

class ModelResponse(BaseModel):
    id: str
    name: str
    base_model_id: Optional[str] = None
    is_active: bool
    created_at: int
    updated_at: int

class ModelsTable:
    def insert_new_model(self, user_id: str, form_data: ModelForm) -> Optional[ModelModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            model = ModelModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": form_data.name,
                    "base_model_id": form_data.base_model_id,
                    "params": form_data.params or {},
                    "meta": {},
                    "access_control": form_data.access_control or {},
                    "is_active": True,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Model(**model.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return model
            else:
                return None

    def get_model_by_id(self, id: str) -> Optional[ModelModel]:
        try:
            with get_db_context() as db:
                model = db.query(Model).filter_by(id=id).first()
                return ModelModel.model_validate(model) if model else None
        except Exception:
            return None

    def get_models_by_user_id(self, user_id: str) -> List[ModelModel]:
        with get_db_context() as db:
            models = db.query(Model).filter_by(user_id=user_id).order_by(Model.created_at.desc()).all()
            return [ModelModel.model_validate(model) for model in models]

    def get_active_models_by_user_id(self, user_id: str) -> List[ModelModel]:
        with get_db_context() as db:
            models = db.query(Model).filter_by(user_id=user_id, is_active=True).order_by(Model.created_at.desc()).all()
            return [ModelModel.model_validate(model) for model in models]

    def get_models_by_base_model_id(self, base_model_id: str) -> List[ModelModel]:
        with get_db_context() as db:
            models = db.query(Model).filter_by(base_model_id=base_model_id).order_by(Model.created_at.desc()).all()
            return [ModelModel.model_validate(model) for model in models]

    def get_public_models(self) -> List[ModelModel]:
        """Get models that are publicly accessible"""
        with get_db_context() as db:
            models = db.query(Model).filter_by(is_active=True).all()
            public_models = []
            for model in models:
                # Check if model is public based on access_control
                if not model.access_control or model.access_control.get("public", False):
                    public_models.append(ModelModel.model_validate(model))
            return public_models

    def get_base_models(self) -> List[ModelModel]:
        """Get models that are base models (no base_model_id)"""
        with get_db_context() as db:
            models = db.query(Model).filter(Model.base_model_id.is_(None)).filter_by(is_active=True).order_by(Model.created_at.desc()).all()
            return [ModelModel.model_validate(model) for model in models]

    def update_model_by_id(self, id: str, updated: dict) -> Optional[ModelModel]:
        try:
            with get_db_context() as db:
                updated["updated_at"] = int(time.time())
                db.query(Model).filter_by(id=id).update(updated)
                db.commit()
                model = db.query(Model).filter_by(id=id).first()
                return ModelModel.model_validate(model) if model else None
        except Exception:
            return None

    def toggle_model_active_by_id(self, id: str) -> Optional[ModelModel]:
        try:
            with get_db_context() as db:
                model = db.query(Model).filter_by(id=id).first()
                if model:
                    model.is_active = not model.is_active
                    model.updated_at = int(time.time())
                    db.commit()
                    return ModelModel.model_validate(model)
                return None
        except Exception:
            return None

    def delete_model_by_id(self, id: str) -> bool:
        try:
            with get_db_context() as db:
                # Update any models that use this as base_model_id to None
                db.query(Model).filter_by(base_model_id=id).update({"base_model_id": None})
                # Delete the model
                db.query(Model).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_models_by_user_id(self, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                # Get all models by user
                user_models = db.query(Model).filter_by(user_id=user_id).all()
                user_model_ids = [model.id for model in user_models]
                
                # Update any models that use these as base_model_id to None
                if user_model_ids:
                    db.query(Model).filter(Model.base_model_id.in_(user_model_ids)).update({"base_model_id": None})
                
                # Delete user's models
                db.query(Model).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def get_model_count_by_user_id(self, user_id: str) -> int:
        with get_db_context() as db:
            return db.query(Model).filter_by(user_id=user_id).count()

    def get_active_model_count_by_user_id(self, user_id: str) -> int:
        with get_db_context() as db:
            return db.query(Model).filter_by(user_id=user_id, is_active=True).count()

Models = ModelsTable()
