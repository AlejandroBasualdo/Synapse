# 3. Usar Keycloak para autenticacion y SSO

Fecha: 2026-09-16

## Estado

Aceptado

## Contexto

El sistema necesita autenticacion con roles distintos (RH, Gerente, Empleado) compartidos entre el frontend y varios microservicios, siguiendo el patron de SSO que se usa en sistemas empresariales reales.

## Decision

Se usa Keycloak, con OAuth2/OIDC como protocolo, integrado en el API Gateway para validar tokens antes de rutear a cada servicio.

Se evaluo Auth0, pero es un servicio comercial con capa gratuita limitada. Keycloak es open source, se puede correr localmente sin costo y sin limites de usuarios, y es el que mas se usa en implementaciones empresariales on-premise o hibridas, que es el escenario que este proyecto busca simular.

## Consecuencias

Keycloak agrega complejidad de configuracion inicial mayor que un servicio gestionado. Esto se documenta con una guia paso a paso en `services/README` cuando se implemente en la fase 4, para que sea reproducible.
