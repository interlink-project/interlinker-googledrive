import os
import motor.motor_asyncio
from app.config import settings

print("bUSCA")
print(settings.MONGODB_URL)
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client.assets