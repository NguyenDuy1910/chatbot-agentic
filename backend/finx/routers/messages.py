import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from finx.constants import ERROR_MESSAGES, SRC_LOG_LEVELS
from finx.models.messages import (
    MessageModel, MessageForm, MessageUpdateForm, Messages,
    MessageReactionModel, MessageReactionForm, MessageReactions
)
from finx.utils.auth import get_verified_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

############################
# Message CRUD Operations
############################

@router.get("/", response_model=List[MessageModel])
async def get_user_messages(
    channel_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_verified_user)
):
    """Get messages with optional filters"""
    try:
        if channel_id:
            return Messages.get_messages_by_channel_id(channel_id, skip, limit)
        elif user_id:
            # Users can only see their own messages unless they're admin
            if user_id != current_user.id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR_MESSAGES.ACCESS_PROHIBITED
                )
            return Messages.get_messages_by_user_id(user_id, skip, limit)
        else:
            # Default to current user's messages
            return Messages.get_messages_by_user_id(current_user.id, skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/{message_id}", response_model=MessageModel)
async def get_message_by_id(message_id: str, current_user=Depends(get_verified_user)):
    """Get a specific message by ID"""
    try:
        message = Messages.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )

        # Users can only see their own messages unless they're admin
        if message.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

        return message
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/", response_model=MessageModel)
async def create_message(
    message_data: MessageForm,
    current_user=Depends(get_verified_user)
):
    """Create a new message"""
    try:
        message = Messages.insert_new_message(current_user.id, message_data)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create message"
            )
        return message
    except Exception as e:
        log.error(f"Error creating message for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{message_id}", response_model=MessageModel)
async def update_message_by_id(
    message_id: str,
    message_data: MessageUpdateForm,
    current_user=Depends(get_verified_user)
):
    """Update an existing message"""
    try:
        # Check if message exists and user owns it
        existing_message = Messages.get_message_by_id(message_id)
        if not existing_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        if existing_message.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Update message
        update_data = message_data.model_dump(exclude_unset=True)
        updated_message = Messages.update_message_by_id(message_id, update_data)
        
        if not updated_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update message"
            )
        
        return updated_message
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{message_id}")
async def delete_message_by_id(message_id: str, current_user=Depends(get_verified_user)):
    """Delete a message"""
    try:
        # Check if message exists and user owns it
        existing_message = Messages.get_message_by_id(message_id)
        if not existing_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        if existing_message.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Delete message (this will also delete replies)
        success = Messages.delete_message_by_id(message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete message"
            )
        
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

############################
# Message Replies
############################

@router.get("/{message_id}/replies", response_model=List[MessageModel])
async def get_message_replies(message_id: str, current_user=Depends(get_verified_user)):
    """Get replies to a specific message"""
    try:
        # Check if parent message exists
        parent_message = Messages.get_message_by_id(message_id)
        if not parent_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        return Messages.get_replies_by_parent_id(message_id)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching replies for message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

############################
# Message Reactions
############################

@router.get("/{message_id}/reactions", response_model=List[MessageReactionModel])
async def get_message_reactions(message_id: str, current_user=Depends(get_verified_user)):
    """Get reactions for a specific message"""
    try:
        # Check if message exists
        message = Messages.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        return MessageReactions.get_reactions_by_message_id(message_id)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching reactions for message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/{message_id}/reactions", response_model=MessageReactionModel)
async def add_message_reaction(
    message_id: str,
    reaction_data: MessageReactionForm,
    current_user=Depends(get_verified_user)
):
    """Add a reaction to a message"""
    try:
        # Check if message exists
        message = Messages.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check if user already reacted with this emoji
        existing_reaction = MessageReactions.get_reaction_by_user_and_message(
            current_user.id, message_id, reaction_data.name
        )
        if existing_reaction:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already reacted with this emoji"
            )
        
        reaction = MessageReactions.insert_new_reaction(current_user.id, message_id, reaction_data)
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )
        
        return reaction
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error adding reaction to message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{message_id}/reactions/{reaction_name}")
async def remove_message_reaction(
    message_id: str,
    reaction_name: str,
    current_user=Depends(get_verified_user)
):
    """Remove a reaction from a message"""
    try:
        # Check if message exists
        message = Messages.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check if reaction exists
        existing_reaction = MessageReactions.get_reaction_by_user_and_message(
            current_user.id, message_id, reaction_name
        )
        if not existing_reaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reaction not found"
            )
        
        success = MessageReactions.delete_reaction_by_user_and_message(
            current_user.id, message_id, reaction_name
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove reaction"
            )
        
        return {"message": "Reaction removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error removing reaction from message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )
