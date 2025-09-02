import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.web.constants.config import ERROR_MESSAGES, SRC_LOG_LEVELS
from src.web.models.prompts import (
    PromptModel, PromptForm, PromptResponse, Prompts
)
from src.web.utils.auth import get_verified_user, get_admin_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

@router.get("/", response_model=List[PromptModel])
async def get_prompts(
    user_only: bool = Query(False, description="Get only current user's prompts"),
    current_user=Depends(get_verified_user)
):
    """Get prompts"""
    try:
        if user_only:
            prompts = Prompts.get_prompts_by_user_id(current_user.id)
        else:
            all_prompts = Prompts.get_prompts()
            # Filter prompts based on access permissions
            prompts = []
            for prompt in all_prompts:
                if _check_prompt_access(prompt, current_user, "read"):
                    prompts.append(prompt)
        
        return prompts
    except Exception as e:
        log.error(f"Error fetching prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/{command}", response_model=PromptResponse)
async def get_prompt(command: str, current_user=Depends(get_verified_user)):
    """Get a specific prompt by command"""
    try:
        prompt = Prompts.get_prompt_by_command(command)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check access permissions
        if not _check_prompt_access(prompt, current_user, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        return PromptResponse(**prompt.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching prompt {command}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/", response_model=PromptModel)
async def create_prompt(
    prompt_data: PromptForm,
    current_user=Depends(get_verified_user)
):
    """Create a new prompt"""
    try:
        # Check if prompt with this command already exists
        existing_prompt = Prompts.get_prompt_by_command(prompt_data.command)
        if existing_prompt:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Prompt with this command already exists"
            )
        
        prompt = Prompts.insert_new_prompt(current_user.id, prompt_data)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create prompt"
            )
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating prompt for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{command}", response_model=PromptModel)
async def update_prompt(
    command: str,
    prompt_data: PromptForm,
    current_user=Depends(get_verified_user)
):
    """Update an existing prompt"""
    try:
        # Check if prompt exists
        existing_prompt = Prompts.get_prompt_by_command(command)
        if not existing_prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions
        if not _check_prompt_access(existing_prompt, current_user, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Update prompt
        updated_prompt = Prompts.update_prompt_by_command(command, prompt_data)
        if not updated_prompt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update prompt"
            )
        
        return updated_prompt
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating prompt {command}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{command}")
async def delete_prompt(command: str, current_user=Depends(get_verified_user)):
    """Delete a prompt"""
    try:
        # Check if prompt exists
        existing_prompt = Prompts.get_prompt_by_command(command)
        if not existing_prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions (only owner or admin can delete)
        if existing_prompt.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Delete prompt
        success = Prompts.delete_prompt_by_command(command)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete prompt"
            )
        
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting prompt {command}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/user/my-prompts", response_model=List[PromptModel])
async def get_my_prompts(current_user=Depends(get_verified_user)):
    """Get current user's prompts"""
    try:
        return Prompts.get_prompts_by_user_id(current_user.id)
    except Exception as e:
        log.error(f"Error fetching user prompts for {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

def _check_prompt_access(prompt: PromptModel, user, access_type: str = "read") -> bool:
    """
    Check if user has access to prompt
    
    Args:
        prompt: Prompt model
        user: Current user
        access_type: "read" or "write"
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Owner always has full access
    if prompt.user_id == user.id:
        return True
    
    # Admin always has full access
    if user.role == "admin":
        return True
    
    # Check access control
    access_control = prompt.access_control
    
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
