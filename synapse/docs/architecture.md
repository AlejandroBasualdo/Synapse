# Arquitectura

## Diagrama de contexto (C4 nivel 1)

Muestra quien usa el sistema y con que sistemas externos habla.

```mermaid
C4Context
  title Contexto del sistema - Synapse

  Person(rh, "Especialista de RH", "Da de alta y gestiona empleados")
  Person(gerente, "Gerente", "Aprueba cambios y revisa reportes")
  Person(empleado, "Empleado", "Consulta su informacion")

  System(platform, "Synapse", "Sistema distribuido de gestion de talento")

  System_Ext(teams, "Microsoft Teams / Outlook", "Notificaciones via Power Automate")
  System_Ext(sftp, "Servidor SFTP externo", "Simula proveedor de beneficios (tipo Wellhub)")

  Rel(rh, platform, "Da de alta empleados, gestiona compensacion")
  Rel(gerente, platform, "Aprueba solicitudes, consulta dashboards")
  Rel(empleado, platform, "Consulta su perfil y beneficios")
  Rel(platform, teams, "Envia notificaciones", "Power Automate")
  Rel(platform, sftp, "Exporta archivo de elegibilidad", "SFTP")
```

## Diagrama de contenedores (C4 nivel 2)

Muestra las piezas internas del sistema y como se comunican.

```mermaid
C4Container
  title Contenedores - Synapse

  Person(rh, "Especialista de RH")

  System_Boundary(platform, "Synapse") {
    Container(frontend, "Frontend Web", "React / Next.js", "Interfaz para RH, gerentes y empleados")
    Container(gateway, "API Gateway", "Traefik", "Punto unico de entrada, ruteo y rate limiting")
    Container(auth, "Keycloak", "OAuth2 / OIDC", "Autenticacion y control de roles")

    Container(employee, "employee-service", "FastAPI", "Datos de empleados, esquema tipo Employee Central")
    Container(comp, "compensation-service", "FastAPI", "Bandas salariales y bono variable")
    Container(benefits, "benefits-service", "FastAPI", "Elegibilidad de beneficios")
    Container(time, "time-attendance-service", "FastAPI", "Asistencia y turnos, esquema tipo UKG")

    Container(bus, "Event Bus", "RabbitMQ", "Comunicacion asincrona entre servicios")
    ContainerDb(dbs, "Bases de datos", "PostgreSQL", "Una base por servicio")

    Container(dwh, "Data Warehouse", "PostgreSQL / DuckDB", "Datos consolidados para analisis")
    Container(mining, "Process Mining", "pm4py", "Descubre y audita procesos desde el log de eventos")
    Container(bi, "Dashboard", "Power BI / Metabase", "KPIs ejecutivos")
  }

  Rel(rh, frontend, "Usa")
  Rel(frontend, gateway, "Llama API", "HTTPS / REST")
  Rel(gateway, auth, "Valida token")
  Rel(gateway, employee, "Rutea")
  Rel(gateway, comp, "Rutea")
  Rel(gateway, benefits, "Rutea")
  Rel(gateway, time, "Rutea")

  Rel(employee, bus, "Publica employee.created")
  Rel(bus, comp, "Consume evento")
  Rel(bus, benefits, "Consume evento")
  Rel(bus, dwh, "Replica eventos")
  Rel(dwh, mining, "Analiza log de eventos")
  Rel(dwh, bi, "Alimenta dashboard")
```

## Notas de diseno

- Cada microservicio tiene su propia base de datos (database per service). No comparten tablas entre si, solo se comunican por eventos o por API.
- El esquema de `employee-service` sigue la estructura publica del OData API de SAP SuccessFactors Employee Central (entidades, foundation objects). No usa ninguna configuracion real de un cliente.
- El esquema de `time-attendance-service` sigue la estructura publica de las APIs de UKG Pro / UKG Ready para asistencia y turnos.
- El bus de eventos es la columna vertebral: cuando `employee-service` publica `employee.created`, los demas servicios reaccionan de forma independiente. Esto evita llamadas sincronas directas entre servicios.
- El log completo de eventos alimenta el modulo de process mining, que descubre el proceso real (no el documentado) y detecta cuellos de botella.

Estos diagramas se actualizan conforme avanza cada fase.
