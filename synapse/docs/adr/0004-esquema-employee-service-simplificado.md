# 4. Esquema de employee-service basado en SAP SuccessFactors EC, con simplificaciones

Fecha: 2026-09-15

## Estado

Aceptado

## Contexto

`employee-service` necesita un esquema de datos de empleados y estructura organizacional.
Se decidio modelarlo sobre la API publica OData v2 (SFOData) de SAP SuccessFactors
Employee Central (documentada en el SAP API Business Hub), reusando los mismos nombres
de entidad y la misma logica de relaciones, para que el proyecto refleje un caso real
de integracion de HRIS sin depender de ninguna configuracion o dato de un cliente real.

Las entidades base elegidas son:

- `PerPerson`: identidad raiz de la persona (fecha de nacimiento, genero).
- `PerPersonal`: datos personales (nombre, estado civil, nacionalidad).
- `PerEmail` / `PerPhone`: medios de contacto.
- `EmpEmployment`: la relacion laboral (fecha de alta/baja, estado).
- `EmpJob`: informacion de puesto (titulo, departamento, centro de costo, ubicacion, jefe).
- Foundation objects: `FODepartment`, `FOCostCenter`, `FOLocation`.

El modelo real de SF EC es "effective-dated": casi todas estas entidades (en especial
`PerPersonal` y `EmpJob`) guardan una fila por cada cambio en el tiempo, con su propia
`startDate`, y la version "vigente" se resuelve consultando la fila con `startDate` mas
reciente que sea menor o igual a la fecha de consulta.

## Decision

Para la fase 1 se simplifica ese modelo effective-dated en dos puntos concretos:

1. **`PerPersonal` no tiene historial**: se guarda un unico registro por persona (el
   estado actual). Un cambio de nombre o estado civil sobrescribe el registro existente.
2. **`EmpJob` es 1:1 con `EmpEmployment`**, no 1:N effective-dated: se guarda solo el
   puesto ACTUAL de cada empleado (titulo, departamento, centro de costo, ubicacion,
   jefe), no el historial completo de cambios de puesto/departamento/compensacion.

En cambio, **`EmpEmployment` si puede tener mas de una fila por persona** (relacion
1:N con `PerPerson`), porque modela un concepto distinto y mas simple: periodos de
contratacion completos (por ejemplo, un caso de recontratacion), no cambios continuos
dentro de un mismo empleo.

La baja de un empleado ("dar de baja") se modela como **baja logica**: se actualiza el
`EmpEmployment` vigente con `employment_status = terminated` y `end_date`, nunca se
borra ningun registro. Esto refleja la practica real de RH (se necesita conservar el
historial de quien trabajo en la empresa y cuando) y evita perder la integridad
referencial de quienes reportaban a esa persona.

El esquema se crea con `SQLAlchemy.metadata.create_all()` (invocado desde el script de
seed), sin una herramienta de migraciones (Alembic). Dado que este es un proyecto de
un solo desarrollador en su fase inicial y el esquema todavia esta cambiando rapido,
el costo de mantener migraciones versionadas no se justifica todavia.

## Consecuencias

- Si una fase futura necesita reconstruir el historial de cambios de puesto (por
  ejemplo, para que el modulo de process mining detecte promociones o transferencias
  entre departamentos), `EmpJob` va a tener que volverse effective-dated (agregar
  `start_date`/`end_date` por fila, o una tabla `EmpJobHistory` separada). Es una
  limitacion conocida y aceptada para esta fase.
- Sin Alembic, cualquier cambio de esquema en fases futuras requiere coordinar a mano
  (recrear la base o migrar datos manualmente). Si el esquema se estabiliza o el
  proyecto necesita desplegarse de forma incremental sin perder datos, se evaluara
  introducir Alembic en ese momento.
- El resto del modelo (nombres de entidad, relaciones, foundation objects) se mantiene
  fiel a la API publica de SF EC, lo que hace mas facil migrar a un modelo
  effective-dated completo despues, sin tener que rediseñar la estructura general.
