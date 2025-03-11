from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.auth import decode_access_token, get_current_user
from models import User
from utils import users

router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/")
async def create_user(user: User):
    user_id = await users.create_user(user)
    return {"id": user_id}


@router.get("/")
async def get_users(current_user: str = Depends(get_current_user)):
    return await users.get_users()


@router.get("/{user_id}")
async def get_user(user: dict = Depends(get_current_user)):
    user = await users.get_user(user["id"])
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}")
async def update_user(user_id: str, user: User):
    updated_count = await users.update_user(user_id, user.dict())
    if updated_count:
        return {"message": "User updated"}
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    deleted_count = await users.delete_user(user_id)
    if deleted_count:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
