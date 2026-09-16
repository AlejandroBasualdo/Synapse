from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import EmploymentStatus, EmploymentType, str_enum


class EmpEmployment(Base):
    """Relacion laboral. Basada en EmpEmployment del modelo OData publico de SF EC.

    Una misma PerPerson puede tener mas de un EmpEmployment a lo largo del tiempo
    (por ejemplo, en un escenario de recontratacion); por eso no es 1:1 con PerPerson.
    """

    __tablename__ = "emp_employment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id_external = Column(String(20), ForeignKey("per_person.person_id_external"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    employment_status = Column(str_enum(EmploymentStatus, 20), nullable=False, default=EmploymentStatus.ACTIVE)
    is_primary = Column(Boolean, nullable=False, default=True)
    termination_reason = Column(String(255), nullable=True)

    person = relationship("PerPerson", back_populates="employments")
    job = relationship(
        "EmpJob",
        back_populates="employment",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="EmpJob.employment_id",
    )


class EmpJob(Base):
    """Informacion de puesto. Basada en EmpJob del modelo OData publico de SF EC.

    Simplificacion respecto al modelo real de SF: se guarda unicamente el puesto
    ACTUAL de cada EmpEmployment (relacion 1:1), no el historial effective-dated
    completo de cambios de puesto/departamento/centro de costo (ver ADR 0004).
    """

    __tablename__ = "emp_job"

    employment_id = Column(Integer, ForeignKey("emp_employment.id"), primary_key=True)
    job_start_date = Column(Date, nullable=False)
    job_title = Column(String(150), nullable=False)
    job_code = Column(String(20), nullable=True)
    department_id = Column(String(20), ForeignKey("fo_department.external_code"), nullable=False)
    cost_center_id = Column(String(20), ForeignKey("fo_cost_center.external_code"), nullable=False)
    location_id = Column(String(20), ForeignKey("fo_location.external_code"), nullable=False)
    manager_employment_id = Column(Integer, ForeignKey("emp_employment.id"), nullable=True)
    employment_type = Column(str_enum(EmploymentType, 20), nullable=False)
    standard_hours = Column(Numeric(5, 2), nullable=False, default=40)

    employment = relationship("EmpEmployment", back_populates="job", foreign_keys=[employment_id])
    department = relationship("FODepartment", back_populates="jobs")
    cost_center = relationship("FOCostCenter", back_populates="jobs")
    location = relationship("FOLocation", back_populates="jobs")
    manager_employment = relationship("EmpEmployment", foreign_keys=[manager_employment_id])
