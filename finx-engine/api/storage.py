"""
Storage layer for datasources and MDL
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import uuid

from api.config import settings


class DataSourceStorage:
    """In-memory storage for datasources with file persistence"""
    
    _datasources: Dict[str, Dict] = {}
    _storage_file = Path(settings.STORAGE_PATH) / "datasources.json"
    
    @classmethod
    def _ensure_storage_dir(cls):
        """Ensure storage directory exists"""
        Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_to_file(cls):
        """Save datasources to file"""
        cls._ensure_storage_dir()
        with open(cls._storage_file, 'w') as f:
            json.dump(cls._datasources, f, indent=2)
    
    @classmethod
    def load_from_file(cls):
        """Load datasources from file"""
        if cls._storage_file.exists():
            with open(cls._storage_file, 'r') as f:
                cls._datasources = json.load(f)
    
    @classmethod
    def create(cls, datasource_data: Dict) -> Dict:
        """Create new datasource"""
        datasource_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        datasource = {
            "id": datasource_id,
            **datasource_data,
            "created_at": now,
            "updated_at": now
        }
        
        cls._datasources[datasource_id] = datasource
        cls.save_to_file()
        return datasource
    
    @classmethod
    def get(cls, datasource_id: str) -> Optional[Dict]:
        """Get datasource by ID"""
        return cls._datasources.get(datasource_id)
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        """List all datasources"""
        return list(cls._datasources.values())
    
    @classmethod
    def update(cls, datasource_id: str, update_data: Dict) -> Optional[Dict]:
        """Update datasource"""
        if datasource_id not in cls._datasources:
            return None
        
        datasource = cls._datasources[datasource_id]
        datasource.update(update_data)
        datasource["updated_at"] = datetime.utcnow().isoformat()
        
        cls.save_to_file()
        return datasource
    
    @classmethod
    def delete(cls, datasource_id: str) -> bool:
        """Delete datasource"""
        if datasource_id in cls._datasources:
            del cls._datasources[datasource_id]
            cls.save_to_file()
            return True
        return False


class MDLStorage:
    """Storage for MDL (Model Definition Language)"""
    
    _mdls: Dict[str, Dict] = {}
    _storage_file = Path(settings.STORAGE_PATH) / "mdls.json"
    
    @classmethod
    def _ensure_storage_dir(cls):
        """Ensure storage directory exists"""
        Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_to_file(cls):
        """Save MDLs to file"""
        cls._ensure_storage_dir()
        with open(cls._storage_file, 'w') as f:
            json.dump(cls._mdls, f, indent=2)
    
    @classmethod
    def load_from_file(cls):
        """Load MDLs from file"""
        if cls._storage_file.exists():
            with open(cls._storage_file, 'r') as f:
                cls._mdls = json.load(f)
    
    @classmethod
    def save(cls, datasource_id: str, mdl: Dict) -> Dict:
        """Save MDL for datasource"""
        mdl_data = {
            "datasource_id": datasource_id,
            **mdl,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        cls._mdls[datasource_id] = mdl_data
        cls.save_to_file()
        return mdl_data
    
    @classmethod
    def get(cls, datasource_id: str) -> Optional[Dict]:
        """Get MDL for datasource"""
        return cls._mdls.get(datasource_id)
    
    @classmethod
    def delete(cls, datasource_id: str) -> bool:
        """Delete MDL for datasource"""
        if datasource_id in cls._mdls:
            del cls._mdls[datasource_id]
            cls.save_to_file()
            return True
        return False
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        """List all MDLs"""
        return list(cls._mdls.values())
