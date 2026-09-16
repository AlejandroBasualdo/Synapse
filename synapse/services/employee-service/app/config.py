from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion del servicio, leida de variables de entorno o de un archivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "employee-service"
    database_url: str = "postgresql://synapse:synapse@localhost:5432/employee_service"


settings = Settings()
