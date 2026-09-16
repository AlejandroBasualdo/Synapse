# employee-service

Servicio de datos de empleados y estructura organizacional. El esquema esta
modelado en la API publica OData v2 (SFOData) de **SAP SuccessFactors Employee
Central**, documentada en el SAP API Business Hub: se reusan los nombres de
entidad y la logica de relaciones, pero todos los datos son sinteticos y no
hay ninguna configuracion real de ninguna empresa.

## Esquema de datos

| Entidad | Basada en | Contenido |
|---|---|---|
| `PerPerson` | `PerPerson` | Identidad raiz: fecha de nacimiento, genero |
| `PerPersonal` | `PerPersonal` | Nombre, estado civil, nacionalidad |
| `PerEmail` / `PerPhone` | `PerEmail` / `PerPhone` | Medios de contacto (1:N por persona) |
| `EmpEmployment` | `EmpEmployment` | Relacion laboral: fecha de alta/baja, estado |
| `EmpJob` | `EmpJob` | Puesto actual: titulo, departamento, centro de costo, ubicacion, jefe |
| `FODepartment` | `FODepartment` | Foundation object: departamento |
| `FOCostCenter` | `FOCostCenter` | Foundation object: centro de costo |
| `FOLocation` | `FOLocation` | Foundation object: ubicacion |

Relaciones principales:

```
PerPerson 1───1 PerPersonal
PerPerson 1───N PerEmail
PerPerson 1───N PerPhone
PerPerson 1───N EmpEmployment   (soporta recontratacion)
EmpEmployment 1───1 EmpJob      (solo el puesto actual, ver Decisiones de modelado)
EmpJob N───1 FODepartment
EmpJob N───1 FOCostCenter
EmpJob N───1 FOLocation
EmpJob N───1 EmpEmployment      (auto-referencia: manager_employment_id)
```

### Decisiones de modelado

El modelo real de SF EC es *effective-dated*: entidades como `PerPersonal` y
`EmpJob` guardan una fila por cada cambio, con su propia fecha de vigencia.
Para esta fase se simplifica:

- **`PerPersonal`** guarda solo el registro actual, sin historial.
- **`EmpJob`** es 1:1 con `EmpEmployment` (solo el puesto vigente), no un
  historial effective-dated de cambios de puesto/departamento.
- **`EmpEmployment`** si permite varias filas por persona, para soportar un
  escenario de recontratacion (es un concepto distinto: periodos de empleo
  completos, no cambios continuos dentro de un mismo empleo).
- **Dar de baja a un empleado es una baja logica**: se marca
  `employment_status = terminated` y se registra `end_date` en el
  `EmpEmployment` vigente. Ningun endpoint borra un empleado fisicamente.

El detalle completo de esta decision, y sus consecuencias para fases futuras
(por ejemplo, si se necesita reconstruir el historial de puestos para el
modulo de process mining), esta documentado en
[docs/adr/0004-esquema-employee-service-simplificado.md](../../docs/adr/0004-esquema-employee-service-simplificado.md).

## Endpoints principales

Documentacion interactiva completa en `/docs` (Swagger UI) una vez que el
servicio esta corriendo. El spec OpenAPI exportado esta en
[docs/api/employee-service.yaml](../../docs/api/employee-service.yaml).

**Empleados**

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/employees` | Alta de empleado (persona + datos personales + puesto) |
| GET | `/employees` | Lista con filtros (`department_id`, `cost_center_id`, `location_id`, `employment_status`, `manager_person_id`) y paginacion |
| GET | `/employees/{person_id_external}` | Detalle completo |
| PATCH | `/employees/{person_id_external}` | Actualiza datos personales y/o de puesto |
| POST | `/employees/{person_id_external}/terminate` | Da de baja (baja logica) |
| GET | `/employees/{person_id_external}/direct-reports` | Reportes directos |

**Estructura organizacional** (mismo patron para `/departments`,
`/cost-centers` y `/locations`): `POST`, `GET` (lista y detalle), `PATCH`.

## Como correrlo localmente

### Con Docker Compose (recomendado)

Desde la raiz del repo:

```bash
docker-compose up --build employee-service employee-db
```

El servicio queda expuesto en `http://localhost:8001` (Swagger en
`http://localhost:8001/docs`). La base de datos no tiene tablas hasta que se
corre el seed:

```bash
docker-compose exec employee-service python -m scripts.seed
```

Esto crea el esquema y genera mas de 50 empleados sinteticos con una
estructura organizacional coherente (5 departamentos, sus centros de costo,
3 ubicaciones, y una jerarquia de reporte de 3 niveles: direccion general,
gerentes de departamento y sus equipos).

### Sin Docker

```bash
cd services/employee-service
python -m venv .venv
.venv/Scripts/activate  # En Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# Contra una instancia local de PostgreSQL:
export DATABASE_URL=postgresql://synapse:synapse@localhost:5432/employee_service
python -m scripts.seed
uvicorn app.main:app --reload
```

### Tests

```bash
pytest
```

Los tests usan SQLite en memoria (no necesitan PostgreSQL corriendo).

### Regenerar el spec OpenAPI

```bash
python -m scripts.export_openapi
```

Sobrescribe `docs/api/employee-service.yaml` con el esquema actual que
expone FastAPI. Se corre a mano despues de cambiar endpoints o schemas.

## Notas

- No hay una herramienta de migraciones (Alembic) en esta fase: el esquema se
  crea con `Base.metadata.create_all()` desde el script de seed. Ver ADR 0004
  para el razonamiento.
- Todos los datos generados por el seed (nombres, correos, telefonos) son
  sinteticos, generados con [Faker](https://faker.readthedocs.io/), y no
  representan a ninguna persona real.
