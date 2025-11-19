"""
MDL Router

Model Definition Language endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from api.models import MDLResponse
from api.storage import MDLStorage

router = APIRouter()


@router.get("/mdl/{datasource_id}", response_model=Dict[str, Any])
async def get_mdl(datasource_id: str):
    """
    Get MDL for a datasource.
    
    Returns the Model Definition Language generated from schema introspection.
    This MDL is used by AI services for schema-aware SQL generation.
    """
    mdl = MDLStorage.get(datasource_id)
    
    if not mdl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for datasource '{datasource_id}'. Run introspection first."
        )
    
    return mdl


@router.put("/mdl/{datasource_id}", response_model=Dict[str, Any])
async def update_mdl(datasource_id: str, mdl_data: Dict[str, Any]):
    """
    Update MDL for a datasource.
    
    Allows manual updates to the generated MDL.
    Useful for adding custom descriptions or fixing metadata.
    """
    existing_mdl = MDLStorage.get(datasource_id)
    
    if not existing_mdl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for datasource '{datasource_id}'"
        )
    
    # Update MDL
    updated_mdl = MDLStorage.save(datasource_id, mdl_data)
    
    return updated_mdl


@router.delete("/mdl/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mdl(datasource_id: str):
    """
    Delete MDL for a datasource.
    
    Removes the generated MDL. You can regenerate it by running introspection again.
    """
    if not MDLStorage.get(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for datasource '{datasource_id}'"
        )
    
    MDLStorage.delete(datasource_id)
    return None


@router.get("/mdl/{datasource_id}/ddl")
async def get_mdl_ddl(datasource_id: str):
    """
    Get DDL representation of MDL.
    
    Returns CREATE TABLE statements generated from MDL.
    Useful for understanding the schema structure.
    """
    mdl = MDLStorage.get(datasource_id)
    
    if not mdl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MDL not found for datasource '{datasource_id}'"
        )
    
    # Generate DDL
    from src.mdl.generator import MDLGenerator
    generator = MDLGenerator()
    ddl = generator.generate_ddl(mdl)
    
    return {
        "datasource_id": datasource_id,
        "ddl": ddl
    }
