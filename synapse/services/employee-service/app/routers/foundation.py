from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.foundation import (
    CostCenterCreate,
    CostCenterResponse,
    CostCenterUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)

router = APIRouter(tags=["organizational-structure"])


# --- Departamentos -----------------------------------------------------------

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    if crud.get_department(db, payload.external_code) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ya existe un departamento con ese external_code")
    return crud.create_department(db, payload)


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return crud.list_departments(db)


@router.get("/departments/{external_code}", response_model=DepartmentResponse)
def get_department(external_code: str, db: Session = Depends(get_db)):
    department = crud.get_department(db, external_code)
    if department is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return department


@router.patch("/departments/{external_code}", response_model=DepartmentResponse)
def update_department(external_code: str, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    department = crud.get_department(db, external_code)
    if department is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return crud.update_department(db, department, payload)


# --- Centros de costo ---------------------------------------------------------

@router.post("/cost-centers", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED)
def create_cost_center(payload: CostCenterCreate, db: Session = Depends(get_db)):
    if crud.get_cost_center(db, payload.external_code) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ya existe un centro de costo con ese external_code")
    return crud.create_cost_center(db, payload)


@router.get("/cost-centers", response_model=list[CostCenterResponse])
def list_cost_centers(db: Session = Depends(get_db)):
    return crud.list_cost_centers(db)


@router.get("/cost-centers/{external_code}", response_model=CostCenterResponse)
def get_cost_center(external_code: str, db: Session = Depends(get_db)):
    cost_center = crud.get_cost_center(db, external_code)
    if cost_center is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Centro de costo no encontrado")
    return cost_center


@router.patch("/cost-centers/{external_code}", response_model=CostCenterResponse)
def update_cost_center(external_code: str, payload: CostCenterUpdate, db: Session = Depends(get_db)):
    cost_center = crud.get_cost_center(db, external_code)
    if cost_center is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Centro de costo no encontrado")
    return crud.update_cost_center(db, cost_center, payload)


# --- Ubicaciones ---------------------------------------------------------------

@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    if crud.get_location(db, payload.external_code) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ya existe una ubicacion con ese external_code")
    return crud.create_location(db, payload)


@router.get("/locations", response_model=list[LocationResponse])
def list_locations(db: Session = Depends(get_db)):
    return crud.list_locations(db)


@router.get("/locations/{external_code}", response_model=LocationResponse)
def get_location(external_code: str, db: Session = Depends(get_db)):
    location = crud.get_location(db, external_code)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
    return location


@router.patch("/locations/{external_code}", response_model=LocationResponse)
def update_location(external_code: str, payload: LocationUpdate, db: Session = Depends(get_db)):
    location = crud.get_location(db, external_code)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
    return crud.update_location(db, location, payload)
