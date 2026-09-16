from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, serializers
from app.database import get_db
from app.models.enums import EmploymentStatus
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeSummary, EmployeeUpdate
from app.schemas.employment import TerminateRequest

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if crud.get_employee(db, payload.person_id_external) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ya existe un empleado con ese person_id_external")
    try:
        person = crud.create_employee(db, payload)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serializers.employee_to_response(person)


@router.get("", response_model=list[EmployeeSummary])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    department_id: str | None = None,
    cost_center_id: str | None = None,
    location_id: str | None = None,
    employment_status: EmploymentStatus | None = None,
    manager_person_id: str | None = None,
    db: Session = Depends(get_db),
):
    people = crud.list_employees(
        db,
        skip=skip,
        limit=limit,
        department_id=department_id,
        cost_center_id=cost_center_id,
        location_id=location_id,
        employment_status=employment_status,
        manager_person_id=manager_person_id,
    )
    return [serializers.employee_to_summary(p) for p in people]


@router.get("/{person_id_external}", response_model=EmployeeResponse)
def get_employee(person_id_external: str, db: Session = Depends(get_db)):
    person = crud.get_employee(db, person_id_external)
    if person is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    return serializers.employee_to_response(person)


@router.patch("/{person_id_external}", response_model=EmployeeResponse)
def update_employee(person_id_external: str, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    person = crud.get_employee(db, person_id_external)
    if person is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    try:
        person = crud.update_employee(db, person, payload)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serializers.employee_to_response(person)


@router.post("/{person_id_external}/terminate", response_model=EmployeeResponse)
def terminate_employee(person_id_external: str, payload: TerminateRequest, db: Session = Depends(get_db)):
    """Da de baja al empleado (baja logica: cambia el estado del employment vigente)."""
    person = crud.get_employee(db, person_id_external)
    if person is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    try:
        person = crud.terminate_employee(db, person, payload)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return serializers.employee_to_response(person)


@router.get("/{person_id_external}/direct-reports", response_model=list[EmployeeSummary])
def get_direct_reports(person_id_external: str, db: Session = Depends(get_db)):
    if crud.get_employee(db, person_id_external) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    reports = crud.get_direct_reports(db, person_id_external)
    return [serializers.employee_to_summary(p) for p in reports]
