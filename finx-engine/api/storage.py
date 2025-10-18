import json
from pathlib import Path
from typing import Dict, Optional, List
from api.config import settings


class DataSourceStorage:
    
    _datasources: Dict[str, Dict] = {}
    
    @classmethod
    def add(cls, datasource_id: str, config: Dict) -> None:
        cls._datasources[datasource_id] = config
    
    @classmethod
    def get(cls, datasource_id: str) -> Optional[Dict]:
        return cls._datasources.get(datasource_id)
    
    @classmethod
    def remove(cls, datasource_id: str) -> bool:
        if datasource_id in cls._datasources:
            del cls._datasources[datasource_id]
            return True
        return False
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        return list(cls._datasources.values())
    
    @classmethod
    def exists(cls, datasource_id: str) -> bool:
        return datasource_id in cls._datasources
    
    @classmethod
    def save_to_file(cls) -> None:
        storage_path = Path(settings.STORAGE_FILE)
        with open(storage_path, 'w') as f:
            json.dump(cls._datasources, f, indent=2)
    
    @classmethod
    def load_from_file(cls) -> None:
        storage_path = Path(settings.STORAGE_FILE)
        if storage_path.exists():
            with open(storage_path, 'r') as f:
                cls._datasources = json.load(f)


class MDLStorage:
    
    @classmethod
    def save(cls, datasource_id: str, mdl: Dict) -> None:
        storage_dir = Path(settings.MDL_STORAGE_DIR)
        storage_dir.mkdir(exist_ok=True)
        
        mdl_path = storage_dir / f"{datasource_id}.json"
        with open(mdl_path, 'w') as f:
            json.dump(mdl, f, indent=2)
    
    @classmethod
    def get(cls, datasource_id: str) -> Optional[Dict]:
        mdl_path = Path(settings.MDL_STORAGE_DIR) / f"{datasource_id}.json"
        if mdl_path.exists():
            with open(mdl_path, 'r') as f:
                return json.load(f)
        return None
    
    @classmethod
    def exists(cls, datasource_id: str) -> bool:
        mdl_path = Path(settings.MDL_STORAGE_DIR) / f"{datasource_id}.json"
        return mdl_path.exists()
    
    @classmethod
    def delete(cls, datasource_id: str) -> bool:
        mdl_path = Path(settings.MDL_STORAGE_DIR) / f"{datasource_id}.json"
        if mdl_path.exists():
            mdl_path.unlink()
            return True
        return False

