from typing import Any
from config import MONGO_URI
from motor import motor_asyncio
import pytz
IST = pytz.timezone("Asia/Kolkata")
client: motor_asyncio.AsyncIOMotorClient[Any] = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
MT = client["Adultbot"]

class dypixx:
    def __init__(self):
        self.users = MT["users"]
        self.banned_users = MT["banned_users"]
        self.cache : dict[int, dict[str, Any]] = {}

    async def addUser(self, user_id: int, name: str) -> dict[str, Any] | None:
        try:
            user: dict[str, Any] = {"user_id": user_id, "name": name}
            await self.users.insert_one(user)
            self.cache[user_id] = user      
            return user
        except Exception as e:
            print("Error in addUser: ", e)
            

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        try:
            if user_id in self.cache:
                return self.cache[user_id]
            user = await self.users.find_one({"user_id": user_id})
            return user
        except Exception as e:
            print("Error in getUser: ", e)
            return None
    
    async def get_all_users(self) -> list[dict[str, Any]]:
        try:
            users : list[dict[str, Any]] = []
            async for user in self.users.find():
                users.append(user)
            return users
        except Exception as e:
            print("Error in getAllUsers: ", e)
            return []

    async def ban_user(self, user_id: int, reason: str = None) -> bool:
        try:
            ban_dypixx = {
                "user_id": user_id,
                "reason": reason
            }
            await self.banned_users.insert_one(ban_dypixx)
            return True
        except Exception as e:
            print("Error in banUser: ", e)
            return False

    async def unban_user(self, user_id: int) -> bool:
        try:
            result = await self.banned_users.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print("Error in unbanUser: ", e)
            return False

    async def is_user_banned(self, user_id: int) -> bool:
        try:
            user = await self.banned_users.find_one({"user_id": user_id})
            return user is not None
        except Exception as e:
            print("Error in isUserBanned: ", e)
            return False

    async def add_promo(self, button_text: str, reply_msg_id: int, promo_text: str, duration_seconds: int) -> dict[str, Any] | None:
        import time
        try:
            expire_at = int(time.time()) + duration_seconds
            promo = {
                "button_text": button_text,
                "reply_msg_id": reply_msg_id,
                "promo_text": promo_text,
                "expire_at": expire_at
            }
            await self.promos.insert_one(promo)
            return promo
        except Exception as e:
            print("Error in add_promo: ", e)
            return None

    async def get_active_promo(self) -> dict[str, Any] | None:
        import time
        try:
            now = int(time.time())
            promo = await self.promos.find_one({"expire_at": {"$gt": now}}, sort=[("expire_at", -1)])
            return promo
        except Exception as e:
            print("Error in get_active_promo: ", e)
            return None

udb = dypixx()
