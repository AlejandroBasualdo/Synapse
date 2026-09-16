# Synapse

Sistema distribuido de gestion de talento (RH) construido con arquitectura de microservicios y orientada a eventos. Incluye un modulo de mineria de procesos que audita y optimiza sus propios flujos a partir del log de eventos que el sistema genera.

## Contexto

Este proyecto nace de mi experiencia real trabajando en integracion de sistemas de RH (SAP SuccessFactors, Wellhub) y mapeo de procesos en Grupo AlEn. Esta construido con especificaciones publicas de API (SAP API Business Hub, documentacion de UKG) y datos sinteticos generados para este proyecto. No contiene informacion de ningun cliente ni empleador.

## Problema que resuelve

Las empresas medianas y grandes operan con varios sistemas de RH que no se hablan entre si de forma nativa (HRIS, beneficios, asistencia, nomina). Este proyecto simula ese ecosistema real: como se integran, que eventos disparan y como se puede auditar el proceso completo despues, en vez de documentarlo a mano.

## Arquitectura

Ver [docs/architecture.md](docs/architecture.md) para los diagramas C4 completos (contexto y contenedores).

## Estado del proyecto

| Fase | Contenido | Estado |
|---|---|---|
| 0 | Diseno de arquitectura y estructura del repo | En progreso |
| 1 | employee-service (esquema tipo Employee Central) | Completa |
| 2 | Bus de eventos + compensation-service + benefits-service | Pendiente |
| 3 | time-attendance-service (esquema tipo UKG) | Pendiente |
| 4 | API Gateway + Keycloak (SSO) | Pendiente |
| 5 | Integraciones externas (Power Automate, SFTP, webhook) | Pendiente |
| 6 | Data warehouse + dashboard | Pendiente |
| 7 | Modulo de process mining | Pendiente |
| 8 | Frontend + CI/CD | Pendiente |
| 9 | Documentacion final y demo | Pendiente |

Seguimiento detallado de tareas en GitHub Projects (por agregar cuando el repo este en GitHub).

## Stack tecnologico

- Backend: Python, FastAPI
- Bases de datos: PostgreSQL (una por servicio), DuckDB para analitica
- Mensajeria: RabbitMQ
- API Gateway: Traefik
- Autenticacion: Keycloak (OAuth2/OIDC)
- Mineria de procesos: pm4py
- Dashboard: Power BI o Metabase
- Frontend: React/Next.js
- Integraciones: Power Automate, SFTP
- Infraestructura: Docker Compose
- CI/CD: GitHub Actions

## Documentacion adicional

- [Diagramas de arquitectura](docs/architecture.md)
- [Decisiones de arquitectura (ADRs)](docs/adr/)
- Especificaciones de API: `docs/api/` (se agregan conforme cada servicio se construye)
- Especificacion de eventos (AsyncAPI): `docs/events/`

## Como correrlo localmente

Por ahora el unico servicio funcional es `employee-service`:

```bash
docker-compose up --build employee-service employee-db
# la primera vez, crea el esquema y carga datos sinteticos:
docker-compose exec employee-service python -m scripts.seed
```

El servicio queda en `http://localhost:8001` (Swagger en `/docs`). Ver
[services/employee-service/README.md](services/employee-service/README.md)
para el detalle del esquema y como correrlo sin Docker.
