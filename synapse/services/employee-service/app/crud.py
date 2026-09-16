from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.employment import EmpEmployment, EmpJob
from app.models.enums import EmploymentStatus
from app.models.foundation import FOCostCenter, FODepartment, FOLocation
from app.models.person import PerEmail, PerPersonal, PerPerson, PerPhone
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.employment import TerminateRequest
from app.schemas.foundation import CostCenterCreate, CostCenterUpdate, DepartmentCreate, DepartmentUpdate, LocationCreate, LocationUpdate


# --- Empleados -------------------------------------------------------------

def _employee_query(db: Session):
    return db.query(PerPerson).options(
        joinedload(PerPerson.personal),
        joinedload(PerPerson.emails),
        joinedload(PerPerson.phones),
        joinedload(PerPerson.employments).joinedload(EmpEmployment.job).joinedload(EmpJob.department),
        joinedload(PerPerson.employments).joinedload(EmpEmployment.job).joinedload(EmpJob.cost_center),
        joinedload(PerPerson.employments).joinedload(EmpEmployment.job).joinedload(EmpJob.location),
        joinedload(PerPerson.employments)
        .joinedload(EmpEmployment.job)
        .joinedload(EmpJob.manager_employment)
        .joinedload(EmpEmployment.person)
        .joinedload(PerPerson.personal),
    )


def get_employee(db: Session, person_id_external: str) -> PerPerson | None:
    return _employee_query(db).filter(PerPerson.person_id_external == person_id_external).first()


def get_primary_employment(person: PerPerson) -> EmpEmployment | None:
    """Devuelve el EmpEmployment vigente (activo mas reciente) o, si no hay ninguno
    activo, el mas reciente en general. Simplificacion util dado que este servicio
    no distingue empleos concurrentes en la practica (ver ADR 0004)."""
    if not person.employments:
        return None
    active = [e for e in person.employments if e.employment_status == EmploymentStatus.ACTIVE]
    pool = active or person.employments
    return max(pool, key=lambda e: e.start_date)


def _resolve_manager_employment_id(db: Session, manager_person_id: str | None) -> int | None:
    if not manager_person_id:
        return None
    manager = get_employee(db, manager_person_id)
    if manager is None:
        raise ValueError(f"manager_person_id '{manager_person_id}' no corresponde a ningun empleado")
    employment = get_primary_employment(manager)
    if employment is None:
        raise ValueError(f"manager_person_id '{manager_person_id}' no tiene un employment activo")
    return employment.id


def list_employees(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    department_id: str | None = None,
    cost_center_id: str | None = None,
    location_id: str | None = None,
    employment_status: EmploymentStatus | None = None,
    manager_person_id: str | None = None,
) -> list[PerPerson]:
    query = _employee_query(db).join(PerPerson.employments).join(EmpEmployment.job)

    if department_id:
        query = query.filter(EmpJob.department_id == department_id)
    if cost_center_id:
        query = query.filter(EmpJob.cost_center_id == cost_center_id)
    if location_id:
        query = query.filter(EmpJob.location_id == location_id)
    if employment_status:
        query = query.filter(EmpEmployment.employment_status == employment_status)
    if manager_person_id:
        manager_employment_ids = select(EmpEmployment.id).where(
            EmpEmployment.person_id_external == manager_person_id
        )
        query = query.filter(EmpJob.manager_employment_id.in_(manager_employment_ids))

    return (
        query.distinct()
        .order_by(PerPerson.person_id_external)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_direct_reports(db: Session, manager_person_id: str) -> list[PerPerson]:
    return list_employees(db, limit=1000, manager_person_id=manager_person_id)


def create_employee(db: Session, payload: EmployeeCreate) -> PerPerson:
    manager_employment_id = _resolve_manager_employment_id(db, payload.job.manager_person_id)

    person = PerPerson(
        person_id_external=payload.person_id_external,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        personal=PerPersonal(**payload.personal.model_dump()),
        emails=[PerEmail(**e.model_dump()) for e in payload.emails],
        phones=[PerPhone(**p.model_dump()) for p in payload.phones],
    )

    job = EmpJob(
        job_start_date=payload.job.job_start_date,
        job_title=payload.job.job_title,
        job_code=payload.job.job_code,
        department_id=payload.job.department_id,
        cost_center_id=payload.job.cost_center_id,
        location_id=payload.job.location_id,
        manager_employment_id=manager_employment_id,
        employment_type=payload.job.employment_type,
        standard_hours=payload.job.standard_hours,
    )
    employment = EmpEmployment(
        start_date=payload.employment.start_date,
        employment_status=EmploymentStatus.ACTIVE,
        is_primary=True,
        job=job,
    )
    person.employments = [employment]

    db.add(person)
    db.commit()
    return get_employee(db, person.person_id_external)


def update_employee(db: Session, person: PerPerson, payload: EmployeeUpdate) -> PerPerson:
    if payload.personal is not None:
        updates = payload.personal.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(person.personal, field, value)

    if payload.job is not None:
        employment = get_primary_employment(person)
        if employment is None or employment.job is None:
            raise ValueError("El empleado no tiene un puesto activo para actualizar")
        job = employment.job
        updates = payload.job.model_dump(exclude_unset=True, exclude={"manager_person_id"})
        for field, value in updates.items():
            setattr(job, field, value)
        if "manager_person_id" in payload.job.model_fields_set:
            job.manager_employment_id = _resolve_manager_employment_id(db, payload.job.manager_person_id)

    db.commit()
    return get_employee(db, person.person_id_external)


def terminate_employee(db: Session, person: PerPerson, payload: TerminateRequest) -> PerPerson:
    """Da de baja al empleado. No borra ningun registro: cambia el estado del
    EmpEmployment vigente a 'terminated' (ver ADR 0004)."""
    employment = get_primary_employment(person)
    if employment is None:
        raise ValueError("El empleado no tiene un employment activo")
    employment.employment_status = EmploymentStatus.TERMINATED
    employment.end_date = payload.end_date
    employment.termination_reason = payload.termination_reason

    db.commit()
    return get_employee(db, person.person_id_external)


# --- Foundation objects ------------------------------------------------------

def get_department(db: Session, external_code: str) -> FODepartment | None:
    return db.get(FODepartment, external_code)


def list_departments(db: Session) -> list[FODepartment]:
    return db.query(FODepartment).order_by(FODepartment.external_code).all()


def create_department(db: Session, payload: DepartmentCreate) -> FODepartment:
    department = FODepartment(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def update_department(db: Session, department: FODepartment, payload: DepartmentUpdate) -> FODepartment:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return department


def get_cost_center(db: Session, external_code: str) -> FOCostCenter | None:
    return db.get(FOCostCenter, external_code)


def list_cost_centers(db: Session) -> list[FOCostCenter]:
    return db.query(FOCostCenter).order_by(FOCostCenter.external_code).all()


def create_cost_center(db: Session, payload: CostCenterCreate) -> FOCostCenter:
    cost_center = FOCostCenter(**payload.model_dump())
    db.add(cost_center)
    db.commit()
    db.refresh(cost_center)
    return cost_center


def update_cost_center(db: Session, cost_center: FOCostCenter, payload: CostCenterUpdate) -> FOCostCenter:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cost_center, field, value)
    db.commit()
    db.refresh(cost_center)
    return cost_center


def get_location(db: Session, external_code: str) -> FOLocation | None:
    return db.get(FOLocation, external_code)


def list_locations(db: Session) -> list[FOLocation]:
    return db.query(FOLocation).order_by(FOLocation.external_code).all()


def create_location(db: Session, payload: LocationCreate) -> FOLocation:
    location = FOLocation(**payload.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def update_location(db: Session, location: FOLocation, payload: LocationUpdate) -> FOLocation:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location
