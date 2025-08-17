import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File as FastAPIFile

from finx.constants import ERROR_MESSAGES, SRC_LOG_LEVELS
from finx.models.files import (
    FileModel, FileForm, FileUpdateForm, Files
)
from finx.utils.auth import get_verified_user, get_admin_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

############################
# File CRUD Operations
############################

@router.get("/", response_model=List[FileModel])
async def get_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_only: bool = Query(True, description="Get only current user's files"),
    current_user=Depends(get_verified_user)
):
    """Get files"""
    try:
        if user_only or current_user.role != "admin":
            return Files.get_files_by_user_id(current_user.id, skip, limit)
        else:
            # For admin, get all users' files (we'll need to implement this differently)
            # For now, just return current user's files
            return Files.get_files_by_user_id(current_user.id, skip, limit)
    except Exception as e:
        log.error(f"Error fetching files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/{file_id}", response_model=FileModel)
async def get_file(file_id: str, current_user=Depends(get_verified_user)):
    """Get a specific file by ID"""
    try:
        file = Files.get_file_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check access permissions
        if not _check_file_access(file, current_user, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        return file
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/", response_model=FileModel)
async def create_file(
    file_data: FileForm,
    current_user=Depends(get_verified_user)
):
    """Create a new file record"""
    try:
        file = Files.insert_new_file(current_user.id, file_data)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file record"
            )
        return file
    except Exception as e:
        log.error(f"Error creating file for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.post("/upload", response_model=FileModel)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user=Depends(get_verified_user)
):
    """Upload a file"""
    try:
        # Read file content
        content = await file.read()
        
        # Create file record
        file_data = FileForm(
            filename=file.filename or "unknown",
            data={"size": len(content), "content_type": file.content_type}
        )
        
        file_record = Files.insert_new_file(current_user.id, file_data)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file record"
            )
        
        # TODO: Save actual file content to storage (filesystem, S3, etc.)
        # For now, we just store metadata
        
        return file_record
    except Exception as e:
        log.error(f"Error uploading file for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.put("/{file_id}", response_model=FileModel)
async def update_file(
    file_id: str,
    file_data: FileUpdateForm,
    current_user=Depends(get_verified_user)
):
    """Update an existing file"""
    try:
        # Check if file exists
        existing_file = Files.get_file_by_id(file_id)
        if not existing_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions
        if not _check_file_access(existing_file, current_user, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Update file
        updated_file = Files.update_file_by_id(file_id, file_data)
        if not updated_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update file"
            )
        
        return updated_file
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user=Depends(get_verified_user)):
    """Delete a file"""
    try:
        # Check if file exists
        existing_file = Files.get_file_by_id(file_id)
        if not existing_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.RESOURCE_NOT_FOUND
            )
        
        # Check write permissions (only owner or admin can delete)
        if existing_file.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )
        
        # Delete file
        success = Files.delete_file_by_id(file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
        
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

############################
# File Search Operations
############################

@router.get("/search/by-hash/{file_hash}", response_model=List[FileModel])
async def get_files_by_hash(file_hash: str, current_user=Depends(get_verified_user)):
    """Get files by hash"""
    try:
        # Use the existing get_file_by_hash method
        file = Files.get_file_by_hash(file_hash)
        files = [file] if file else []

        # Filter files based on access permissions
        accessible_files = []
        for file in files:
            if _check_file_access(file, current_user, "read"):
                accessible_files.append(file)
        return accessible_files
    except Exception as e:
        log.error(f"Error searching files by hash {file_hash}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

@router.get("/search/by-filename/{filename}", response_model=List[FileModel])
async def get_files_by_filename(filename: str, current_user=Depends(get_verified_user)):
    """Get files by filename"""
    try:
        files = Files.get_files_by_filename(filename)
        # Filter files based on access permissions
        accessible_files = []
        for file in files:
            if _check_file_access(file, current_user, "read"):
                accessible_files.append(file)
        return accessible_files
    except Exception as e:
        log.error(f"Error searching files by filename {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

############################
# Admin Operations
############################

@router.delete("/admin/all")
async def delete_all_files(current_user=Depends(get_admin_user)):
    """Delete all files (admin only)"""
    try:
        # For now, we'll just return a message since we don't have a delete_all method
        # In a real implementation, you'd want to add this method to the Files model
        return {"message": "Delete all files operation not implemented yet"}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting all files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

############################
# Helper Functions
############################

def _check_file_access(file: FileModel, user, access_type: str = "read") -> bool:
    """
    Check if user has access to file
    
    Args:
        file: File model
        user: Current user
        access_type: "read" or "write"
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Owner always has full access
    if file.user_id == user.id:
        return True
    
    # Admin always has full access
    if user.role == "admin":
        return True
    
    # Check access control
    access_control = file.access_control
    
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
    
    return False
