import motor.motor_asyncio
from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client.data
collection = db[settings.COLLECTION_NAME]