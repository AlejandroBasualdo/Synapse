import enum

from sqlalchemy import Enum as SAEnum


def str_enum(enum_cls: type[enum.Enum], length: int):
    """Columna Enum que persiste el .value del enum (ej. "full_time") en vez del
    .name (ej. "FULL_TIME"), para que el dato crudo en la base coincida con lo que
    expone la API."""
    return SAEnum(enum_cls, native_enum=False, length=length, values_callable=lambda obj: [e.value for e in obj])


class Gender(str, enum.Enum):
    """Codigos de genero tal como los usa el picklist estandar de SF EC (PerPerson.gender)."""

    M = "M"
    F = "F"
    O = "O"
    U = "U"


class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    OTHER = "other"


class EmailType(str, enum.Enum):
    BUSINESS = "business"
    PERSONAL = "personal"


class PhoneType(str, enum.Enum):
    MOBILE = "mobile"
    LANDLINE = "landline"
    WORK = "work"
    HOME = "home"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    TERMINATED = "terminated"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTINGENT = "contingent"


class FoundationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
