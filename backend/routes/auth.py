from fastapi import APIRouter, HTTPException, Depends
from database import users_collection
from utils.users import serialize_user
from utils.auth import verify_password, create_jwt_token
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
async def login(data: dict):
    """Authenticate user and return JWT + user ID"""
    email = data.get("email")
    password = data.get("password")

    # Fetch user by email
    user = await users_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    token, expire = create_jwt_token({"id": str(user["_id"]), "email": user["email"]})

    # Return both token and user ID
    return {"token": token, "id": str(user["_id"]), "exp": expire}


@router.post("/logout")
async def logout():
    return {"message": "Logout successful"}
