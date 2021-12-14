from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.utils.crudbase import CRUDBase
from app.model import DriveAsset
import app.crud as crud
from app.old.schemas import DriveAssetCreate, DriveAssetUpdate
import uuid
from app.google import copy_file, create_file

class CRUDDriveAsset(CRUDBase[DriveAsset, DriveAssetCreate, DriveAssetUpdate]):
    def create(self, db: Session, *, path: Optional[str]) -> DriveAsset:
        file = create_file(path, "Copy")
        drive_id=file["id"]
        work_link = file["webViewLink"]
        download_link = file["webContentLink"] 

        db_obj = DriveAsset(
            work_link=work_link,
            download_link=download_link,
            drive_id=drive_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def clone(self, db: Session, *, id: Optional[uuid.UUID]) -> DriveAsset:
        db_driveasset = self.get(db=db, id=id)
        # TODO: verify that exists
        file = copy_file("Copy", db_driveasset.drive_id)
        
        drive_id=file["id"]
        work_link = file["webViewLink"]
        download_link = file["webContentLink"] 

        db_obj = DriveAsset(
            work_link=work_link,
            download_link=download_link,
            drive_id=drive_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: uuid.UUID) -> DriveAsset:
        obj = db.query(DriveAsset).get(id)
        db.delete(obj)
        db.commit()
        # TODO: remove from drive if needed
        return obj


driveasset = CRUDDriveAsset(DriveAsset)