import logging
from datetime import timedelta

from src.web.models.auths import (
    Auths,
    SigninForm,
    SignupForm,
    SigninResponse,
    UpdatePasswordForm,
    UpdateProfileForm,
    UserResponse,
)
from src.web.models.users import Users
from src.web.constants.config import ERROR_MESSAGES, SRC_LOG_LEVELS
from src.web.utils.auth import (
    create_token,
    get_current_user,
    get_authenticated_user
)

from fastapi import APIRouter, Depends, HTTPException, Response, status

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()


@router.post("/register", response_model=SigninResponse)
async def register_user(response: Response, form_data: SignupForm):
    # Check if user already exists
    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.EMAIL_TAKEN,
        )
    try:
        # Create new user
        role = "admin" if Users.get_num_users() == 0 else "pending"
        user = Auths.insert_new_auth(
            form_data.email.lower(),
            form_data.password,
            form_data.name,
            form_data.profile_image_url,
            role,
        )

        if user:
            # Create access token
            token = create_token(
                data={"id": user.id},
                expires_delta=timedelta(days=1)
            )

            # Set cookie
            response.set_cookie(
                key="token",
                value=token,
                httponly=True,
                secure=True,
                samesite="lax"
            )

            return SigninResponse(
                token=token,
                token_type="Bearer",
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                profile_image_url=user.profile_image_url,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.CREATE_USER_ERROR,
            )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(str(err)),
        )



@router.post("/login", response_model=SigninResponse)
async def login_user(response: Response, form_data: SigninForm):
    user = Auths.authenticate_user(form_data.email.lower(), form_data.password)
    if user:
        # Create access token
        token = create_token(
            data={"id": user.id},
            expires_delta=timedelta(days=1)
        )

        # Set cookie
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        return SigninResponse(
            token=token,
            token_type="Bearer",
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            profile_image_url=user.profile_image_url,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_CRED,
        )


@router.post("/logout")
async def logout_user(response: Response, user=Depends(get_current_user)):
    """
    User logout endpoint
    """
    response.delete_cookie("token")
    return {"message": "Successfully signed out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_session(user=Depends(get_authenticated_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        profile_image_url=user.profile_image_url,
    )


@router.put("/me/profile", response_model=UserResponse)
async def update_user_profile(form_data: UpdateProfileForm, user=Depends(get_authenticated_user)):
    updated_user = Users.update_user_by_id(
        user.id,
        {
            "profile_image_url": form_data.profile_image_url,
            "name": form_data.name,
        },
    )

    if updated_user:
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name,
            role=updated_user.role,
            profile_image_url=updated_user.profile_image_url,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )


@router.put("/me/password", response_model=bool)
async def update_user_password(form_data: UpdatePasswordForm, user=Depends(get_authenticated_user)):
    """
    Update user password
    """
    # Verify current password by authenticating user
    auth_user = Auths.authenticate_user(user.email, form_data.password)
    if auth_user:
        # Update password
        result = Auths.update_user_password_by_id(user.id, form_data.new_password)
        if result:
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.DEFAULT(),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_PASSWORD,
        )
