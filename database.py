from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.video_encoder_bot
        self.users = self.db.users
        self.settings = self.db.settings
        self.queue = self.db.queue
        self.premium = self.db.premium
        self.fsub_channels = self.db.fsub_channels
        
    # User operations
    async def add_user(self, user_id):
        """Add new user to database"""
        try:
            user_data = {
                "user_id": user_id,
                "joined_date": datetime.now(),
                "total_encodings": 0,
                "last_used": datetime.now()
            }
            await self.users.update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            
    async def is_user_exist(self, user_id):
        """Check if user exists"""
        user = await self.users.find_one({"user_id": user_id})
        return bool(user)
        
    async def total_users_count(self):
        """Get total users count"""
        count = await self.users.count_documents({})
        return count
        
    async def update_user_activity(self, user_id):
        """Update user's last activity"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_used": datetime.now()}}
        )
        
    async def increment_encoding_count(self, user_id):
        """Increment user's encoding count"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"total_encodings": 1}}
        )
        
    # Settings operations
    async def set_thumbnail(self, user_id, file_id):
        """Save user's thumbnail"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": {"thumbnail": file_id}},
            upsert=True
        )
        
    async def get_thumbnail(self, user_id):
        """Get user's thumbnail"""
        data = await self.settings.find_one({"user_id": user_id})
        return data.get("thumbnail") if data else None
        
    async def delete_thumbnail(self, user_id):
        """Delete user's thumbnail"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$unset": {"thumbnail": ""}}
        )
        
    async def set_watermark(self, user_id, watermark_text):
        """Save user's watermark text"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": {"watermark": watermark_text}},
            upsert=True
        )
        
    async def get_watermark(self, user_id):
        """Get user's watermark"""
        data = await self.settings.find_one({"user_id": user_id})
        return data.get("watermark") if data else None
        
    async def set_media_type(self, user_id, media_type):
        """Set preferred media type (video/document)"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": {"media_type": media_type}},
            upsert=True
        )
        
    async def get_media_type(self, user_id):
        """Get user's preferred media type"""
        data = await self.settings.find_one({"user_id": user_id})
        return data.get("media_type", "video") if data else "video"
        
    async def toggle_spoiler(self, user_id):
        """Toggle spoiler mode"""
        data = await self.settings.find_one({"user_id": user_id})
        current = data.get("spoiler", False) if data else False
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": {"spoiler": not current}},
            upsert=True
        )
        return not current
        
    async def get_spoiler(self, user_id):
        """Get spoiler setting"""
        data = await self.settings.find_one({"user_id": user_id})
        return data.get("spoiler", False) if data else False
        
    async def set_upload_mode(self, user_id, mode):
        """Set upload mode"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": {"upload_mode": mode}},
            upsert=True
        )
        
    async def get_upload_mode(self, user_id):
        """Get upload mode"""
        data = await self.settings.find_one({"user_id": user_id})
        return data.get("upload_mode", "default") if data else "default"
        
    # Queue operations
    async def add_to_queue(self, user_id, task_data):
        """Add task to queue"""
        task = {
            "user_id": user_id,
            "task_data": task_data,
            "status": "pending",
            "added_time": datetime.now()
        }
        result = await self.queue.insert_one(task)
        return str(result.inserted_id)
        
    async def get_queue_position(self, task_id):
        """Get position in queue"""
        tasks = await self.queue.find({"status": "pending"}).sort("added_time", 1).to_list(length=None)
        for i, task in enumerate(tasks, 1):
            if str(task["_id"]) == task_id:
                return i
        return 0
        
    async def get_total_queue(self):
        """Get total queue count"""
        count = await self.queue.count_documents({"status": "pending"})
        return count
        
    async def update_queue_status(self, task_id, status):
        """Update queue task status"""
        from bson.objectid import ObjectId
        await self.queue.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": status}}
        )
        
    async def clear_queue(self):
        """Clear all pending queue tasks"""
        await self.queue.delete_many({"status": "pending"})
        
    async def get_next_task(self):
        """Get next pending task"""
        task = await self.queue.find_one(
            {"status": "pending"},
            sort=[("added_time", 1)]
        )
        return task
        
    # Premium users operations
    async def add_premium_user(self, user_id, days):
        """Add premium user"""
        expiry = datetime.now() + timedelta(days=days)
        await self.premium.update_one(
            {"user_id": user_id},
            {"$set": {"expiry_date": expiry}},
            upsert=True
        )
        
    async def is_premium_user(self, user_id):
        """Check if user is premium"""
        data = await self.premium.find_one({"user_id": user_id})
        if not data:
            return False
        if data["expiry_date"] < datetime.now():
            await self.premium.delete_one({"user_id": user_id})
            return False
        return True
        
    async def get_premium_users(self):
        """Get all premium users"""
        users = await self.premium.find().to_list(length=None)
        return users
        
    async def remove_premium_user(self, user_id):
        """Remove premium user"""
        await self.premium.delete_one({"user_id": user_id})
        
    # Force subscribe operations
    async def add_fsub_channel(self, channel_id):
        """Add force subscribe channel"""
        await self.fsub_channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"channel_id": channel_id}},
            upsert=True
        )
        
    async def delete_fsub_channel(self, channel_id):
        """Delete force subscribe channel"""
        await self.fsub_channels.delete_one({"channel_id": channel_id})
        
    async def get_fsub_channels(self):
        """Get all force subscribe channels"""
        channels = await self.fsub_channels.find().to_list(length=None)
        return [ch["channel_id"] for ch in channels]
        
    # Admin settings
    async def set_bot_setting(self, key, value):
        """Set bot setting"""
        await self.settings.update_one(
            {"_id": "bot_settings"},
            {"$set": {key: value}},
            upsert=True
        )
        
    async def get_bot_setting(self, key, default=None):
        """Get bot setting"""
        data = await self.settings.find_one({"_id": "bot_settings"})
        return data.get(key, default) if data else default
