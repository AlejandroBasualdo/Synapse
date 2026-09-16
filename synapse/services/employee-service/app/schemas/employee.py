from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmploymentStatus, Gender
from app.schemas.employment import EmploymentInfo, JobInfo, JobInfoUpdate
from app.schemas.foundation import CostCenterResponse, DepartmentResponse, LocationResponse
from app.schemas.person import (
    EmailCreate,
    EmailResponse,
    PersonalInfo,
    PersonalInfoUpdate,
    PhoneCreate,
    PhoneResponse,
)


class EmployeeCreate(BaseModel):
    person_id_external: str
    date_of_birth: date
    gender: Gender
    personal: PersonalInfo
    emails: list[EmailCreate] = []
    phones: list[PhoneCreate] = []
    employment: EmploymentInfo
    job: JobInfo


class EmployeeUpdate(BaseModel):
    personal: PersonalInfoUpdate | None = None
    job: JobInfoUpdate | None = None


class ManagerSummary(BaseModel):
    person_id_external: str
    full_name: str


class JobResponse(BaseModel):
    job_start_date: date
    job_title: str
    job_code: str | None
    employment_type: str
    standard_hours: float
    department: DepartmentResponse
    cost_center: CostCenterResponse
    location: LocationResponse
    manager: ManagerSummary | None = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    person_id_external: str
    date_of_birth: date
    gender: Gender
    first_name: str
    last_name: str
    middle_name: str | None
    salutation: str | None
    marital_status: str | None
    nationality: str | None
    emails: list[EmailResponse] = []
    phones: list[PhoneResponse] = []
    employment_status: EmploymentStatus
    hire_date: date
    termination_date: date | None
    job: JobResponse | None


class EmployeeSummary(BaseModel):
    """Version liviana del empleado, usada en listados."""

    person_id_external: str
    full_name: str
    job_title: str | None
    department_id: str | None
    employment_status: EmploymentStatus
