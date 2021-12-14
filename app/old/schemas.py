from typing import Optional, List


from pydantic import BaseModel
from datetime import datetime
import uuid

# Shared properties
class DriveAssetBase(BaseModel):
    pass

# Properties to receive on driveasset creation
class DriveAssetCreate(DriveAssetBase):
    pass


# Properties to receive on driveasset update
class DriveAssetUpdate(DriveAssetBase):
    pass


# Properties shared by models stored in DB
class DriveAssetInDBBase(DriveAssetBase):
    # id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# Properties to return to client
class DriveAsset(DriveAssetInDBBase):
    # drive_id: str
    work_link: str
    download_link: str
    modified_time: str
    icon_link: str
    thumbnail_link: str
    size: str

# Properties to return to client after create

class DriveAssetOnCreate(DriveAssetInDBBase):
    id: uuid.UUID
    
# Properties properties stored in DB
class DriveAssetInDB(DriveAssetInDBBase):
    pass
