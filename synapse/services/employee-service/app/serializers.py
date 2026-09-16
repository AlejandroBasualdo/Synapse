from app.crud import get_primary_employment
from app.models.employment import EmpEmployment
from app.models.person import PerPerson
from app.schemas.employee import EmployeeResponse, EmployeeSummary, JobResponse, ManagerSummary
from app.schemas.foundation import CostCenterResponse, DepartmentResponse, LocationResponse


def _job_response(employment: EmpEmployment | None) -> JobResponse | None:
    job = employment.job if employment else None
    if job is None:
        return None

    manager = None
    if job.manager_employment and job.manager_employment.person:
        manager_person = job.manager_employment.person
        manager = ManagerSummary(
            person_id_external=manager_person.person_id_external,
            full_name=f"{manager_person.personal.first_name} {manager_person.personal.last_name}",
        )

    return JobResponse(
        job_start_date=job.job_start_date,
        job_title=job.job_title,
        job_code=job.job_code,
        employment_type=job.employment_type.value,
        standard_hours=float(job.standard_hours),
        department=DepartmentResponse.model_validate(job.department),
        cost_center=CostCenterResponse.model_validate(job.cost_center),
        location=LocationResponse.model_validate(job.location),
        manager=manager,
    )


def employee_to_response(person: PerPerson) -> EmployeeResponse:
    employment = get_primary_employment(person)
    return EmployeeResponse(
        person_id_external=person.person_id_external,
        date_of_birth=person.date_of_birth,
        gender=person.gender,
        first_name=person.personal.first_name,
        last_name=person.personal.last_name,
        middle_name=person.personal.middle_name,
        salutation=person.personal.salutation,
        marital_status=person.personal.marital_status.value if person.personal.marital_status else None,
        nationality=person.personal.nationality,
        emails=list(person.emails),
        phones=list(person.phones),
        employment_status=employment.employment_status,
        hire_date=employment.start_date,
        termination_date=employment.end_date,
        job=_job_response(employment),
    )


def employee_to_summary(person: PerPerson) -> EmployeeSummary:
    employment = get_primary_employment(person)
    job = employment.job if employment else None
    return EmployeeSummary(
        person_id_external=person.person_id_external,
        full_name=f"{person.personal.first_name} {person.personal.last_name}",
        job_title=job.job_title if job else None,
        department_id=job.department_id if job else None,
        employment_status=employment.employment_status,
    )
