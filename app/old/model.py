import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.google import get_file_by_id
from app.utils.base_class import Base
from sqlalchemy_utils import observes
from werkzeug.utils import cached_property

class DriveAsset(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_id = Column(String, nullable=True)
    
    work_link = Column(String, nullable=True)
    download_link = Column(String, nullable=True)
    
    """
    PROBLEM: modified tyme and size are dynamic
    
    modified_time = Column(String, nullable=True)
    icon_link = Column(String, nullable=True)
    thumbnail_link = Column(String, nullable=True)
    size = Column(String, nullable=True)

    
    @cached_property
    def file(self):
        f: dict = get_file_by_id(self.drive_id)
        return f

    @observes('drive_id')
    def fileId_observer(self, asset):
        f = self.file
        self.work_link = f.get("webViewLink", "")
        self.download_link = f.get("webContentLink", "")
        self.modified_time = f.get("modifiedTime", "")
        self.icon_link = f.get("iconLink", "")
        self.thumbnail_link = f.get("thumbnailLink", "")
        self.size = f.get("size", "")
    """
    @cached_property
    def file(self):
        f: dict = get_file_by_id(self.drive_id)
        return f

    @property
    def modified_time(self):
        return self.file.get("modifiedTime", "")

    @property
    def icon_link(self):
        return self.file.get("iconLink", "")

    @property
    def thumbnail_link(self):
        return self.file.get("thumbnailLink", "")

    @property
    def size(self):
        return self.file.get("size", "")
