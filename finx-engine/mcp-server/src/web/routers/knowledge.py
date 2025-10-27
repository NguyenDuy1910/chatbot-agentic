import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.web.constants.config import ERROR_MESSAGES, SRC_LOG_LEVELS
from src.web.models.knowledge import (
    KnowledgeModel, KnowledgeForm, KnowledgeResponse, Knowledges
)
from src.web.utils.auth import get_verified_user, get_admin_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

@router.get("/", response_model=List[KnowledgeModel])
async def get_knowledge_bases(
    user_only: bool = Query(False, description="Get only current user's knowledge bases"),
    current_user=Depends(get_verified_user)
):
    """Get knowledge bases"""
    try:
        if user_only or current_user.role != "admin":
            return Knowledges.get_knowledge_bases_by_user_id(current_user.id)
        else:
            return Knowledges.get_knowledge_bases()
    except Exception as e:
        log.error(f"Error fetching knowledge bases: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge_base(knowledge_id: str, current_user=Depends(get_verified_user)):
    """Get a specific knowledge base by ID"""
    try:
        knowledge = Knowledges.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check access permissions
        if not _check_knowledge_access(knowledge, current_user, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Convert to response model (could include files in the future)
        return KnowledgeResponse(**knowledge.model_dump(), files=[])
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching knowledge base {knowledge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/", response_model=KnowledgeModel)
async def create_knowledge_base(
    knowledge_data: KnowledgeForm,
    current_user=Depends(get_verified_user)
):
    """Create a new knowledge base"""
    try:
        knowledge = Knowledges.insert_new_knowledge(current_user.id, knowledge_data)
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create knowledge base"
            )
        return knowledge
    except Exception as e:
        log.error(f"Error creating knowledge base for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{knowledge_id}", response_model=KnowledgeModel)
async def update_knowledge_base(
    knowledge_id: str,
    knowledge_data: KnowledgeForm,
    current_user=Depends(get_verified_user)
):
    """Update an existing knowledge base"""
    try:
        # Check if knowledge base exists
        existing_knowledge = Knowledges.get_knowledge_by_id(knowledge_id)
        if not existing_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions
        if not _check_knowledge_access(existing_knowledge, current_user, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Update knowledge base
        updated_knowledge = Knowledges.update_knowledge_by_id(knowledge_id, knowledge_data)
        if not updated_knowledge:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update knowledge base"
            )
        
        return updated_knowledge
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating knowledge base {knowledge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{knowledge_id}")
async def delete_knowledge_base(knowledge_id: str, current_user=Depends(get_verified_user)):
    """Delete a knowledge base"""
    try:
        # Check if knowledge base exists
        existing_knowledge = Knowledges.get_knowledge_by_id(knowledge_id)
        if not existing_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions (only owner or admin can delete)
        if existing_knowledge.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Delete knowledge base
        success = Knowledges.delete_knowledge_by_id(knowledge_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete knowledge base"
            )
        
        return {"message": "Knowledge base deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting knowledge base {knowledge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{knowledge_id}/data")
async def update_knowledge_data(
    knowledge_id: str,
    data: dict,
    current_user=Depends(get_verified_user)
):
    """Update knowledge base data"""
    try:
        # Check if knowledge base exists
        existing_knowledge = Knowledges.get_knowledge_by_id(knowledge_id)
        if not existing_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions
        if not _check_knowledge_access(existing_knowledge, current_user, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Update knowledge data
        updated_knowledge = Knowledges.update_knowledge_data_by_id(knowledge_id, data)
        if not updated_knowledge:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update knowledge data"
            )
        
        return {"message": "Knowledge data updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating knowledge data {knowledge_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/admin/all")
async def delete_all_knowledge_bases(current_user=Depends(get_admin_user)):
    """Delete all knowledge bases (admin only)"""
    try:
        success = Knowledges.delete_all_knowledge()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete all knowledge bases"
            )
        
        return {"message": "All knowledge bases deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting all knowledge bases: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

def _check_knowledge_access(knowledge: KnowledgeModel, user, access_type: str = "read") -> bool:
    """
    Check if user has access to knowledge base
    
    Args:
        knowledge: Knowledge base model
        user: Current user
        access_type: "read" or "write"
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Owner always has full access
    if knowledge.user_id == user.id:
        return True
    
    # Admin always has full access
    if user.role == "admin":
        return True
    
    # Check access control
    access_control = knowledge.access_control
    
    # If access_control is None, it's public (read access for all users)
    if access_control is None:
        return access_type == "read" and user.role in ["user", "admin"]
    
    # If access_control is empty dict, it's private (owner only)
    if not access_control:
        return False
    
    # Check specific permissions
    permissions = access_control.get(access_type, {})
    
    # Check user-specific permissions
    allowed_users = permissions.get("user_ids", [])
    if user.id in allowed_users:
        return True
    
    # Check group-specific permissions (would need to implement group membership check)
    # allowed_groups = permissions.get("group_ids", [])
    # if any(group_id in user.groups for group_id in allowed_groups):
    #     return True
    
    return False
