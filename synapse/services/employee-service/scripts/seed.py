"""
Script de seed: genera datos sinteticos de empleados y estructura organizacional
para desarrollo y demo. Todos los nombres, correos, telefonos y fechas se generan
con Faker; no representan a ninguna persona real.

Uso:
    python -m scripts.seed
"""
import random
from datetime import date, timedelta

from faker import Faker

from app.database import SessionLocal, create_tables
from app.models.employment import EmpEmployment, EmpJob
from app.models.enums import EmailType, EmploymentStatus, EmploymentType, FoundationStatus, Gender, MaritalStatus, PhoneType
from app.models.foundation import FOCostCenter, FODepartment, FOLocation
from app.models.person import PerEmail, PerPersonal, PerPerson, PerPhone

fake = Faker("es_MX")
Faker.seed(42)
random.seed(42)

DEPARTMENTS = [
    ("DEP-1000", "Recursos Humanos"),
    ("DEP-2000", "Tecnologia"),
    ("DEP-3000", "Ventas"),
    ("DEP-4000", "Finanzas"),
    ("DEP-5000", "Operaciones"),
]

LOCATIONS = [
    ("LOC-100", "Oficina Ciudad de Mexico", "Ciudad de Mexico", "MX"),
    ("LOC-200", "Oficina Monterrey", "Monterrey", "MX"),
    ("LOC-300", "Oficina Remota", "Remoto", "MX"),
]

JOB_TITLES = {
    "DEP-1000": ["Especialista de RH", "Analista de Nomina", "Reclutador"],
    "DEP-2000": ["Desarrollador de Software", "Analista QA", "DevOps Engineer", "Arquitecto de Software"],
    "DEP-3000": ["Ejecutivo de Ventas", "Gerente de Cuenta", "Analista Comercial"],
    "DEP-4000": ["Analista Financiero", "Contador", "Analista de Tesoreria"],
    "DEP-5000": ["Coordinador de Operaciones", "Analista de Procesos", "Supervisor de Planta"],
}

TOTAL_EMPLOYEES_TARGET = 60

_person_counter = 0


def _next_person_id() -> str:
    global _person_counter
    _person_counter += 1
    return f"E{10000000 + _person_counter}"


def _random_birthdate():
    return fake.date_of_birth(minimum_age=22, maximum_age=60)


def _random_hire_date(max_years_ago: int = 8):
    days_ago = random.randint(30, 365 * max_years_ago)
    return date.today() - timedelta(days=days_ago)


def seed_foundation_objects(db):
    departments = []
    for code, name in DEPARTMENTS:
        department = FODepartment(external_code=code, name=name, status=FoundationStatus.ACTIVE)
        db.add(department)
        departments.append(department)

    cost_centers = []
    for code, name in DEPARTMENTS:
        cc_code = code.replace("DEP", "CC")
        cost_center = FOCostCenter(external_code=cc_code, name=f"CeCo {name}", status=FoundationStatus.ACTIVE)
        db.add(cost_center)
        cost_centers.append(cost_center)

    locations = []
    for code, name, city, country in LOCATIONS:
        location = FOLocation(external_code=code, name=name, city=city, country=country, status=FoundationStatus.ACTIVE)
        db.add(location)
        locations.append(location)

    db.commit()
    return departments, cost_centers, locations


def _create_person(db, *, department_code, cost_center_code, location_code, job_title, employment_type, manager_employment_id, hire_date):
    person_id = _next_person_id()
    gender = random.choice(list(Gender))
    first_name = fake.first_name_male() if gender == Gender.M else fake.first_name_female()
    last_name = f"{fake.last_name()} {fake.last_name()}"

    person = PerPerson(
        person_id_external=person_id,
        date_of_birth=_random_birthdate(),
        gender=gender,
        personal=PerPersonal(
            first_name=first_name,
            last_name=last_name,
            marital_status=random.choice(list(MaritalStatus)),
            nationality="MX",
        ),
    )

    email_local = f"{first_name}.{last_name}".lower().replace(" ", ".")
    person.emails = [
        PerEmail(email_type=EmailType.BUSINESS, email_address=f"{email_local}@synapse-demo.com", is_primary=True),
        PerEmail(email_type=EmailType.PERSONAL, email_address=fake.free_email(), is_primary=False),
    ]
    person.phones = [
        PerPhone(phone_type=PhoneType.MOBILE, phone_number=fake.msisdn()[-10:], is_primary=True),
    ]

    job = EmpJob(
        job_start_date=hire_date,
        job_title=job_title,
        department_id=department_code,
        cost_center_id=cost_center_code,
        location_id=location_code,
        manager_employment_id=manager_employment_id,
        employment_type=employment_type,
        standard_hours=40 if employment_type == EmploymentType.FULL_TIME else 20,
    )
    employment = EmpEmployment(
        start_date=hire_date,
        employment_status=EmploymentStatus.ACTIVE,
        is_primary=True,
        job=job,
    )
    person.employments = [employment]

    db.add(person)
    db.flush()  # asigna employment.id para poder usarlo como manager de otras personas
    return person, employment


def seed_employees(db, locations):
    location_codes = [loc.external_code for loc in locations]

    ceo_person, ceo_employment = _create_person(
        db,
        department_code=DEPARTMENTS[0][0],
        cost_center_code=DEPARTMENTS[0][0].replace("DEP", "CC"),
        location_code=location_codes[0],
        job_title="Director General",
        employment_type=EmploymentType.FULL_TIME,
        manager_employment_id=None,
        hire_date=_random_hire_date(max_years_ago=10),
    )

    total_created = 1
    remaining = TOTAL_EMPLOYEES_TARGET - 1
    per_department = remaining // len(DEPARTMENTS)

    for dept_code, dept_name in DEPARTMENTS:
        cc_code = dept_code.replace("DEP", "CC")

        _head_person, head_employment = _create_person(
            db,
            department_code=dept_code,
            cost_center_code=cc_code,
            location_code=random.choice(location_codes),
            job_title=f"Gerente de {dept_name}",
            employment_type=EmploymentType.FULL_TIME,
            manager_employment_id=ceo_employment.id,
            hire_date=_random_hire_date(max_years_ago=9),
        )
        total_created += 1

        for _ in range(per_department - 1):
            employment_type = random.choices(
                [EmploymentType.FULL_TIME, EmploymentType.PART_TIME, EmploymentType.CONTINGENT],
                weights=[0.8, 0.1, 0.1],
            )[0]
            _create_person(
                db,
                department_code=dept_code,
                cost_center_code=cc_code,
                location_code=random.choice(location_codes),
                job_title=random.choice(JOB_TITLES[dept_code]),
                employment_type=employment_type,
                manager_employment_id=head_employment.id,
                hire_date=_random_hire_date(),
            )
            total_created += 1

    db.commit()
    return total_created


def main():
    print("Creando esquema (si no existe)...")
    create_tables()
    db = SessionLocal()
    try:
        print("Creando foundation objects (departamentos, centros de costo, ubicaciones)...")
        _departments, _cost_centers, locations = seed_foundation_objects(db)
        print("Creando empleados sinteticos...")
        total = seed_employees(db, locations)
        print(f"Listo: {total} empleados creados.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
