from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: abre una sesion por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables(bind=None):
    """Crea el esquema a partir de los modelos. No se usa en el arranque del servicio
    (ver ADR 0004) sino explicitamente desde el script de seed o en tests.

    Importa app.models aqui (no arriba del modulo) para evitar un ciclo de imports
    con app.database, y para garantizar que todos los modelos quedaron registrados
    en Base.metadata sin importar si el caller ya los importo o no.
    """
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=bind or engine)
