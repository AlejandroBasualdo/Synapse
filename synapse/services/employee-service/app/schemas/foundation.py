from pydantic import BaseModel, ConfigDict

from app.models.enums import FoundationStatus


class DepartmentCreate(BaseModel):
    external_code: str
    name: str
    status: FoundationStatus = FoundationStatus.ACTIVE


class DepartmentUpdate(BaseModel):
    name: str | None = None
    status: FoundationStatus | None = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_code: str
    name: str
    status: FoundationStatus


class CostCenterCreate(BaseModel):
    external_code: str
    name: str
    status: FoundationStatus = FoundationStatus.ACTIVE


class CostCenterUpdate(BaseModel):
    name: str | None = None
    status: FoundationStatus | None = None


class CostCenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_code: str
    name: str
    status: FoundationStatus


class LocationCreate(BaseModel):
    external_code: str
    name: str
    city: str
    country: str
    status: FoundationStatus = FoundationStatus.ACTIVE


class LocationUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    country: str | None = None
    status: FoundationStatus | None = None


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_code: str
    name: str
    city: str
    country: str
    status: FoundationStatus
