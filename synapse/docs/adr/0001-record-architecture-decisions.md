# 1. Registrar decisiones de arquitectura

Fecha: 2026-09-16

## Estado

Aceptado

## Contexto

Este proyecto va a tomar decisiones tecnicas importantes (mensajeria, autenticacion, gateway, etc) a lo largo de varias fases. Sin un registro, se pierde el por que de cada decision y es dificil justificarlas despues, tanto para quien retome el proyecto como en una entrevista de trabajo.

## Decision

Se usan Architecture Decision Records (ADR) en formato Michael Nygard. Cada decision tecnica relevante se documenta en un archivo numerado dentro de `docs/adr/`, con las secciones: Estado, Contexto, Decision, Consecuencias.

## Consecuencias

Cada cambio de tecnologia o de enfoque queda trazado. El costo es escribir un archivo corto por cada decision importante, lo cual es minimo comparado con el valor de tener el razonamiento documentado.
