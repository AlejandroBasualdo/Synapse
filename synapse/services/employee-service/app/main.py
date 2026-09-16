from fastapi import FastAPI

from app.routers import employees, foundation

app = FastAPI(
    title="employee-service",
    description=(
        "Servicio de datos de empleados y estructura organizacional. Esquema modelado "
        "en la API publica OData v2 (SFOData) de SAP SuccessFactors Employee Central: "
        "PerPerson, PerPersonal, EmpEmployment, EmpJob y los foundation objects "
        "FODepartment, FOCostCenter y FOLocation. No usa datos ni configuracion real "
        "de ninguna empresa."
    ),
    version="0.1.0",
)

app.include_router(employees.router)
app.include_router(foundation.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
