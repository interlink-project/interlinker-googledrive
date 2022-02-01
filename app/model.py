from pydantic import BaseModel, Field
from typing import Optional

fields = "id, name, webContentLink, webViewLink, thumbnailLink, version, mimeType, size, iconLink, createdTime, modifiedTime"

mime_types = {
    "docs": "application/vnd.google-apps.document",
    "drawing": "application/vnd.google-apps.drawing",
    "file": "application/vnd.google-apps.file",
    "folder": "application/vnd.google-apps.folder",
    "form": "application/vnd.google-apps.form",
    "fusiontable": "application/vnd.google-apps.fusiontable",
    "map": "application/vnd.google-apps.map",
    "slide": "application/vnd.google-apps.presentation",
    "script": "application/vnd.google-apps.script",
    "site": "application/vnd.google-apps.site",
    "spreadsheet": "application/vnd.google-apps.spreadsheet",
}
mime_type_options = mime_types.keys()


class AssetSchema(BaseModel):
    id: str = Field(..., alias='_id')
    temporal: Optional[bool] = True
    name: Optional[str]
    webContentLink: Optional[str]
    webViewLink: Optional[str]
    thumbnailLink: Optional[str]
    version: Optional[str]
    mimeType: Optional[str]
    size: Optional[str]
    iconLink: Optional[str]
    createdTime: Optional[str]
    modifiedTime: Optional[str]


class AssetCreateSchema(BaseModel):
    mime_type : str
    name : str

class AssetFromGoogleId(BaseModel):
    id: str