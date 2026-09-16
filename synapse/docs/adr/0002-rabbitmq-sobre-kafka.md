# 2. Usar RabbitMQ en lugar de Kafka como bus de eventos

Fecha: 2026-09-16

## Estado

Aceptado

## Contexto

El sistema necesita comunicacion asincrona entre 4 microservicios. Las opciones evaluadas fueron RabbitMQ y Kafka, las dos mas usadas en el mercado.

## Decision

Se usa RabbitMQ.

Kafka esta pensado para volumenes muy altos de eventos y para casos donde se necesita reproducir el log completo de eventos historicos como fuente de verdad (event sourcing a gran escala). Este proyecto tiene un numero pequeno de servicios y un volumen de eventos bajo, mas cercano a un patron de notificacion y orquestacion entre servicios. RabbitMQ cubre ese caso con menor complejidad operativa y es mas rapido de levantar y mantener en un entorno de un solo desarrollador.

## Consecuencias

Si en una fase futura el proyecto necesita reproducir el historial completo de eventos para el modulo de process mining a gran escala, se evaluara migrar o complementar con Kafka. Por ahora, el log de eventos para process mining se persiste por separado en el data warehouse, no depende de la retencion de RabbitMQ.
