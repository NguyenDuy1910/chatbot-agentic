from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models import MDLResponse
from api.storage import MDLStorage, DataSourceStorage

router = APIRouter()


@router.get("/mdl/{datasource_id}", response_model=MDLResponse)
async def get_mdl(datasource_id: str):
    if not DataSourceStorage.exists(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    mdl = MDLStorage.get(datasource_id)
    if not mdl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for data source '{datasource_id}'. Run introspection first."
        )
    
    return MDLResponse(datasource_id=datasource_id, mdl=mdl)


@router.get("/mdl/{datasource_id}/download")
async def download_mdl(datasource_id: str):
    if not DataSourceStorage.exists(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    mdl = MDLStorage.get(datasource_id)
    if not mdl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for data source '{datasource_id}'. Run introspection first."
        )
    
    mdl_json = json.dumps(mdl, indent=2)
    
    return Response(
        content=mdl_json,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={datasource_id}_mdl.json"
        }
    )


@router.delete("/mdl/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mdl(datasource_id: str):
    if not MDLStorage.delete(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for data source '{datasource_id}'"
        )

