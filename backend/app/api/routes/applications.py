from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    Application,
    ApplicationCreate,
    ApplicationStats,
    ApplicationStatus,
    ApplicationUpdate,
)
from app.services import application_service

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[Application])
def get_applications(
    search: Optional[str] = None, status: Optional[ApplicationStatus] = None
):
    return application_service.list_applications(search=search, status=status)


@router.get("/stats", response_model=ApplicationStats)
def get_stats():
    return application_service.get_stats()


@router.get("/{application_id}", response_model=Application)
def get_application(application_id: str):
    application = application_service.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post("", response_model=Application, status_code=201)
def create_application(payload: ApplicationCreate):
    return application_service.create_application(payload)


@router.put("/{application_id}", response_model=Application)
def update_application(application_id: str, payload: ApplicationUpdate):
    application = application_service.update_application(application_id, payload)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: str):
    deleted = application_service.delete_application(application_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
