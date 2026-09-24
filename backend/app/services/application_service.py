import json
import uuid
from datetime import datetime
from threading import Lock
from typing import Optional

from app.config import APPLICATIONS_FILE
from app.models.schemas import (
    Application,
    ApplicationCreate,
    ApplicationStats,
    ApplicationStatus,
    ApplicationUpdate,
)

_file_lock = Lock()


def _read_all() -> list[dict]:
    with _file_lock:
        if not APPLICATIONS_FILE.exists():
            return []
        content = APPLICATIONS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else []


def _write_all(records: list[dict]) -> None:
    with _file_lock:
        APPLICATIONS_FILE.write_text(
            json.dumps(records, indent=2, default=str), encoding="utf-8"
        )


def list_applications(
    search: Optional[str] = None, status: Optional[ApplicationStatus] = None
) -> list[Application]:
    records = _read_all()

    if status:
        records = [r for r in records if r["status"] == status.value]

    if search:
        term = search.lower()
        records = [
            r
            for r in records
            if term in r["company"].lower() or term in r["role"].lower()
        ]

    records.sort(key=lambda r: r["created_at"], reverse=True)
    return [Application(**r) for r in records]


def get_application(application_id: str) -> Optional[Application]:
    for record in _read_all():
        if record["id"] == application_id:
            return Application(**record)
    return None


def create_application(payload: ApplicationCreate) -> Application:
    records = _read_all()
    now = datetime.utcnow().isoformat()
    record = {
        "id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        **payload.model_dump(mode="json"),
    }
    records.append(record)
    _write_all(records)
    return Application(**record)


def update_application(
    application_id: str, payload: ApplicationUpdate
) -> Optional[Application]:
    records = _read_all()
    for record in records:
        if record["id"] == application_id:
            updates = payload.model_dump(mode="json", exclude_unset=True)
            record.update(updates)
            record["updated_at"] = datetime.utcnow().isoformat()
            _write_all(records)
            return Application(**record)
    return None


def delete_application(application_id: str) -> bool:
    records = _read_all()
    remaining = [r for r in records if r["id"] != application_id]
    if len(remaining) == len(records):
        return False
    _write_all(remaining)
    return True


def get_stats() -> ApplicationStats:
    records = _read_all()
    counts = {status.value: 0 for status in ApplicationStatus}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1

    return ApplicationStats(
        total=len(records),
        applied=counts[ApplicationStatus.APPLIED.value],
        shortlisted=counts[ApplicationStatus.SHORTLISTED.value],
        interview=counts[ApplicationStatus.INTERVIEW.value],
        selected=counts[ApplicationStatus.SELECTED.value],
        rejected=counts[ApplicationStatus.REJECTED.value],
    )
