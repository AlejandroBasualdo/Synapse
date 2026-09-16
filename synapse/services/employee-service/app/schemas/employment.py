from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import EmploymentType


class EmploymentInfo(BaseModel):
    start_date: date


class JobInfo(BaseModel):
    job_start_date: date
    job_title: str
    job_code: str | None = None
    department_id: str
    cost_center_id: str
    location_id: str
    manager_person_id: str | None = None
    employment_type: EmploymentType
    standard_hours: Decimal = Decimal("40.00")


class JobInfoUpdate(BaseModel):
    job_title: str | None = None
    job_code: str | None = None
    department_id: str | None = None
    cost_center_id: str | None = None
    location_id: str | None = None
    manager_person_id: str | None = None
    employment_type: EmploymentType | None = None
    standard_hours: Decimal | None = None


class TerminateRequest(BaseModel):
    end_date: date
    termination_reason: str | None = None
