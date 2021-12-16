from pydantic import BaseModel, Field
from typing import Optional

fields = "id, name, webContentLink, webViewLink, thumbnailLink, version, mimeType, size, iconLink, createdTime, modifiedTime"

class AssetSchema(BaseModel):
    id: str = Field(..., alias='_id')
    name: Optional[str]
    webContentLink: str = Field(..., min_length=3)
    webViewLink: str = Field(..., min_length=3)
    thumbnailLink: Optional[str]
    version: Optional[str]
    mimeType: Optional[str]
    size: Optional[str]
    iconLink: Optional[str]
    createdTime: Optional[str]
    modifiedTime: Optional[str]