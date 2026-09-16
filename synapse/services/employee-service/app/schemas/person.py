from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import EmailType, MaritalStatus, PhoneType


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    middle_name: str | None = None
    salutation: str | None = None
    marital_status: MaritalStatus | None = None
    nationality: str | None = None


class PersonalInfoUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    salutation: str | None = None
    marital_status: MaritalStatus | None = None
    nationality: str | None = None


class EmailCreate(BaseModel):
    email_type: EmailType
    email_address: EmailStr
    is_primary: bool = False


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email_type: EmailType
    email_address: EmailStr
    is_primary: bool


class PhoneCreate(BaseModel):
    phone_type: PhoneType
    phone_number: str
    is_primary: bool = False


class PhoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_type: PhoneType
    phone_number: str
    is_primary: bool
