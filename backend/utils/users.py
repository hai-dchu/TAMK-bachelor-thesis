from bson import ObjectId
from database import users_collection
from models import User
from utils.auth import hash_password, verify_password
from bson import ObjectId

def serialize_user(user):
    return {
        "id": str(user["_id"]),
        **{k: v for k, v in user.items() if (k != "_id" and k != "password")}
    }


async def create_user(user: User):
    user.password = hash_password(user.password)  # Hash password before storing
    new_user = await users_collection.insert_one(user.dict())
    return str(new_user.inserted_id)


async def get_user_by_email(email: str):
    user = await users_collection.find_one({"email": email})
    if user:
        return {**user, "id": str(user["_id"])}
    return None


async def get_users():
    users = await users_collection.find().to_list(100)
    return [serialize_user(user) for user in users]


async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return serialize_user(user)
    return None


async def update_user(user_id: str, user_data: dict):
    result = await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    return result.modified_count


async def delete_user(user_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count
