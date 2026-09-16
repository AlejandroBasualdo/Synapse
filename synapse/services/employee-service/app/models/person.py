from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import EmailType, Gender, MaritalStatus, PhoneType, str_enum


class PerPerson(Base):
    """Entidad raiz de identidad de una persona. Basada en PerPerson del modelo OData
    publico de SAP SuccessFactors Employee Central."""

    __tablename__ = "per_person"

    person_id_external = Column(String(20), primary_key=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(str_enum(Gender, 1), nullable=False)

    personal = relationship("PerPersonal", back_populates="person", uselist=False, cascade="all, delete-orphan")
    emails = relationship("PerEmail", back_populates="person", cascade="all, delete-orphan")
    phones = relationship("PerPhone", back_populates="person", cascade="all, delete-orphan")
    employments = relationship("EmpEmployment", back_populates="person", cascade="all, delete-orphan")


class PerPersonal(Base):
    """Datos personales (nombre, estado civil, nacionalidad). Basada en PerPersonal.

    Simplificacion respecto al modelo real de SF: se guarda unicamente el registro
    ACTUAL, sin el historial effective-dated completo (ver ADR 0004).
    """

    __tablename__ = "per_personal"

    person_id_external = Column(String(20), ForeignKey("per_person.person_id_external"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    salutation = Column(String(20), nullable=True)
    marital_status = Column(str_enum(MaritalStatus, 20), nullable=True)
    nationality = Column(String(2), nullable=True)

    person = relationship("PerPerson", back_populates="personal")


class PerEmail(Base):
    """Correo electronico de la persona. Basada en PerEmail."""

    __tablename__ = "per_email"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id_external = Column(String(20), ForeignKey("per_person.person_id_external"), nullable=False)
    email_type = Column(str_enum(EmailType, 20), nullable=False)
    email_address = Column(String(255), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

    person = relationship("PerPerson", back_populates="emails")


class PerPhone(Base):
    """Telefono de la persona. Basada en PerPhone."""

    __tablename__ = "per_phone"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id_external = Column(String(20), ForeignKey("per_person.person_id_external"), nullable=False)
    phone_type = Column(str_enum(PhoneType, 20), nullable=False)
    phone_number = Column(String(30), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

    person = relationship("PerPerson", back_populates="phones")
