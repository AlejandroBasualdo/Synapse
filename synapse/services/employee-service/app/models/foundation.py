from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import FoundationStatus, str_enum


class FODepartment(Base):
    """Foundation object de departamento. Basado en FODepartment del modelo OData
    publico de SAP SuccessFactors Employee Central."""

    __tablename__ = "fo_department"

    external_code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(str_enum(FoundationStatus, 10), nullable=False, default=FoundationStatus.ACTIVE)

    jobs = relationship("EmpJob", back_populates="department")


class FOCostCenter(Base):
    """Foundation object de centro de costo. Basado en FOCostCenter."""

    __tablename__ = "fo_cost_center"

    external_code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(str_enum(FoundationStatus, 10), nullable=False, default=FoundationStatus.ACTIVE)

    jobs = relationship("EmpJob", back_populates="cost_center")


class FOLocation(Base):
    """Foundation object de ubicacion. Basado en FOLocation."""

    __tablename__ = "fo_location"

    external_code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(2), nullable=False)
    status = Column(str_enum(FoundationStatus, 10), nullable=False, default=FoundationStatus.ACTIVE)

    jobs = relationship("EmpJob", back_populates="location")
