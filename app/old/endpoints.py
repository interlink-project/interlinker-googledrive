
import uuid
from typing import Any, List, Union

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app import crud
from app.old import schemas
from app.utils import deps
from fastapi import File, UploadFile
import os
router = APIRouter()

@router.get("/", response_model=List[schemas.DriveAsset])
def read_driveassets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve driveassets.
    """
    driveassets = crud.driveasset.get_multi(db, skip=skip, limit=limit)
    return driveassets


@router.post("/", response_model=schemas.DriveAssetOnCreate)
def create_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
) -> Any:
    try:
        os.mkdir("tmp")
    except Exception as e:
        pass
    file_name = os.getcwd()+"/tmp/"+file.filename.replace(" ", "-")
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
        
    asset = crud.driveasset.create(db=db, path=file_name)
    os.remove(file_name)
    return asset

@router.post("/{id}/clone", response_model=schemas.DriveAssetOnCreate)
def clone_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
) -> Any:
    return crud.driveasset.clone(db=db, id=id)
    
@router.put("/{id}", response_model=schemas.DriveAsset)
def update_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    driveasset_in: schemas.DriveAssetUpdate,
) -> Any:
    """
    Update an driveasset.
    """
    driveasset = crud.driveasset.get(db=db, id=id)
    if not driveasset:
        raise HTTPException(status_code=404, detail="DriveAsset not found")
    driveasset = crud.driveasset.update(db=db, db_obj=driveasset, obj_in=driveasset_in)
    return driveasset


@router.get("/{id}", response_model=schemas.DriveAsset)
def read_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
) -> Any:
    """
    Get driveasset by ID.
    """
    driveasset = crud.driveasset.get(db=db, id=id)
    if not driveasset:
        raise HTTPException(status_code=404, detail="DriveAsset not found")
    return driveasset


@router.delete("/{id}", response_model=schemas.DriveAsset)
def delete_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
) -> Any:
    """
    Delete an driveasset.
    """
    driveasset = crud.driveasset.get(db=db, id=id)
    if not driveasset:
        raise HTTPException(status_code=404, detail="DriveAsset not found")
    driveasset = crud.driveasset.remove(db=db, id=id)
    return driveasset

@router.put("/{id}/gui")
def gui_driveasset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
) -> Any:
    """
    Update an driveasset.
    """
    driveasset = crud.driveasset.get(db=db, id=id)
    if not driveasset:
        raise HTTPException(status_code=404, detail="DriveAsset not found")
    return RedirectResponse(driveasset.work_link)