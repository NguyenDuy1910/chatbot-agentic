import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.web.constants.config import ERROR_MESSAGES, SRC_LOG_LEVELS
from src.web.models.chats import (
    ChatModel, ChatForm, ChatUpdateForm, Chats,
    FolderModel, FolderForm, FolderUpdateForm, Folders
)
from src.web.utils.auth import get_verified_user, get_current_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

@router.get("/", response_model=List[ChatModel])
async def get_user_chats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    archived: Optional[bool] = Query(None),
    pinned: Optional[bool] = Query(None),
    folder_id: Optional[str] = Query(None),
    current_user=Depends(get_verified_user)
):
    """Get chats for the current user with optional filters"""
    try:
        if archived is True:
            return Chats.get_archived_chats_by_user_id(current_user.id)
        elif pinned is True:
            return Chats.get_pinned_chats_by_user_id(current_user.id)
        elif folder_id is not None:
            return Chats.get_chats_by_folder_id(folder_id, current_user.id)
        else:
            return Chats.get_chats_by_user_id(current_user.id, skip, limit)
    except Exception as e:
        log.error(f"Error fetching chats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/{chat_id}", response_model=ChatModel)
async def get_chat_by_id(chat_id: str, current_user=Depends(get_verified_user)):
    """Get a specific chat by ID"""
    try:
        chat = Chats.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        # Check if user owns the chat
        if chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        return chat
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/", response_model=ChatModel)
async def create_chat(
    chat_data: ChatForm,
    current_user=Depends(get_verified_user)
):
    """Create a new chat"""
    try:
        chat = Chats.insert_new_chat(current_user.id, chat_data)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chat"
            )
        return chat
    except Exception as e:
        log.error(f"Error creating chat for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{chat_id}", response_model=ChatModel)
async def update_chat_by_id(
    chat_id: str,
    chat_data: ChatUpdateForm,
    current_user=Depends(get_verified_user)
):
    """Update an existing chat"""
    try:
        # Check if chat exists and user owns it
        existing_chat = Chats.get_chat_by_id(chat_id)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        if existing_chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        # Update chat
        update_data = chat_data.model_dump(exclude_unset=True)
        updated_chat = Chats.update_chat_by_id(chat_id, update_data)

        if not updated_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chat"
            )

        return updated_chat
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{chat_id}")
async def delete_chat_by_id(chat_id: str, current_user=Depends(get_verified_user)):
    """Delete a chat"""
    try:
        # Check if chat exists and user owns it
        existing_chat = Chats.get_chat_by_id(chat_id)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        if existing_chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        # Delete chat
        success = Chats.delete_chat_by_id(chat_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chat"
            )

        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{chat_id}/archive", response_model=ChatModel)
async def toggle_chat_archive_status(chat_id: str, current_user=Depends(get_verified_user)):
    """Toggle chat archive status"""
    try:
        # Check if chat exists and user owns it
        existing_chat = Chats.get_chat_by_id(chat_id)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        if existing_chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        updated_chat = Chats.toggle_chat_archive_by_id(chat_id)
        if not updated_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle chat archive"
            )

        return updated_chat
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error toggling archive for chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{chat_id}/pin", response_model=ChatModel)
async def toggle_chat_pin_status(chat_id: str, current_user=Depends(get_verified_user)):
    """Toggle chat pin status"""
    try:
        # Check if chat exists and user owns it
        existing_chat = Chats.get_chat_by_id(chat_id)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        if existing_chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        updated_chat = Chats.toggle_chat_pin_by_id(chat_id)
        if not updated_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle chat pin"
            )

        return updated_chat
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error toggling pin for chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/shared/{share_id}", response_model=ChatModel)
async def get_shared_chat(share_id: str):
    """Get a shared chat by share ID (no authentication required)"""
    try:
        chat = Chats.get_chat_by_share_id(share_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        return chat
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching shared chat {share_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/{chat_id}/share")
async def share_chat_by_id(
    chat_id: str,
    share_id: Optional[str] = None,
    current_user=Depends(get_verified_user)
):
    """Share a chat or update its share ID"""
    try:
        # Check if chat exists and user owns it
        existing_chat = Chats.get_chat_by_id(chat_id)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        if existing_chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        updated_chat = Chats.update_chat_share_id_by_id(chat_id, share_id)
        if not updated_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chat share"
            )

        return {"message": "Chat share updated successfully", "share_id": share_id}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error sharing chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )
