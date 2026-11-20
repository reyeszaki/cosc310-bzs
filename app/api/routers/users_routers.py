from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import bearer, get_current_user, require_role, user_service
from app.schema.users_schema import CreateUser, LoginRequest, LoginResponse, UpdateUser, UserPublic

router = APIRouter(tags=["accounts"])


@router.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer",
    responses={409: {"description": "Email already registered"}},
)
def register(request: CreateUser) -> UserPublic:
    try:
        return user_service.register(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Sign in and receive a bearer token",
    responses={401: {"description": "Invalid email or password, or account deactivated"}},
)
def login(request: LoginRequest) -> LoginResponse:
    try:
        return user_service.login(request)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sign out and invalidate the current token",
    responses={401: {"description": "Not authenticated"}},
)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    user: UserPublic = Depends(get_current_user),
) -> Response:
    user_service.logout(credentials.credentials)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/users/me",
    response_model=UserPublic,
    summary="Get the signed-in customer's profile",
    responses={401: {"description": "Not authenticated"}},
)
def get_me(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return user


@router.put(
    "/users/me",
    response_model=UserPublic,
    summary="Update the signed-in customer's details or delivery address",
    responses={
        401: {"description": "Not authenticated"},
        409: {"description": "Email already registered"},
    },
)
def update_me(request: UpdateUser, user: UserPublic = Depends(get_current_user)) -> UserPublic:
    try:
        return user_service.update_user(user.id, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post(
    "/users/me/deactivate",
    response_model=UserPublic,
    summary="Deactivate the signed-in customer's account",
    responses={401: {"description": "Not authenticated"}},
)
def deactivate_me(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return user_service.deactivate_user(user.id)


@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="Get any user by ID (admin only)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not allowed for this role"},
        404: {"description": "User not found"},
    },
)
def get_user(user_id: int, admin: UserPublic = Depends(require_role("admin"))) -> UserPublic:
    try:
        return user_service.get_user(user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))