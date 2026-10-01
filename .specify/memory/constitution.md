<!--
Sync Impact Report
==================
- Version change: N/A (scaffold sin ratificar) → 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] → I. Simplicidad y Legibilidad
  - [PRINCIPLE_2_NAME] → II. Cobertura de Tests Automatizados
  - [PRINCIPLE_3_NAME] → III. Validación de Entrada
  - [PRINCIPLE_4_NAME] → IV. Credenciales en Variables de Entorno
  - [PRINCIPLE_5_NAME] → V. Manejo de Errores con Códigos HTTP Correctos
  - (nuevo) → VI. Documentación y Comentarios en Español
  - (nuevo) → VII. Solo Datos Ficticios en Pruebas
- Added sections:
  - Estándares de Calidad (antes: [SECTION_2_NAME] sin rellenar)
  - Flujo de Desarrollo (antes: [SECTION_3_NAME] sin rellenar)
- Removed sections: ninguna
- Follow-up TODOs: ninguno (todos los placeholders resueltos)
-->

# sdd-demo Constitution

## Core Principles

### I. Simplicidad y Legibilidad (NO NEGOCIABLE)

El código simple y legible MUST anteponerse a la ingeniosidad:

- Se MUST preferir la solución directa y fácil de leer sobre la clever o
  excesivamente optimizada; no se introducen abstracciones prematuras.
- Todo bloque de código MUST ser comprensible por otra persona sin
  explicación adicional: nombres descriptivos, funciones cortas y flujo
  de control evidente.
- La ingeniosidad solo se acepta si aporta un beneficio medible y está
  justificada con un comentario que explique el porqué.

Rationale: el coste real del software está en el mantenimiento; el código
simple reduce defectos, acelera las revisiones y facilita los cambios.

### II. Cobertura de Tests Automatizados (NO NEGOCIABLE)

Toda funcionalidad MUST tener tests automatizados:

- Ninguna funcionalidad se considera terminada sin tests automatizados que
  pasen de forma verificable en la canalización de integración.
- Los tests MUST cubrir el comportamiento esperado y los casos límite y
  de error relevantes.
- Un cambio que rompa un test existente MUST bloquear su fusión hasta
  repararlo o justificarlo explícitamente en la revisión.

Rationale: sin tests automatizados no hay evidencia objetiva de que el
comportamiento es el esperado ni de que los cambios no rompen lo existente.

### III. Validación de Entrada

Todos los datos de entrada MUST validarse antes de usarse:

- Los datos recibidos (parámetros de ruta, query, cuerpo de la petición,
  cabeceras relevantes, archivos) MUST validarse en los límites del
  sistema: tipo, formato, rango y longitud.
- Un dato inválido MUST rechazarse con un mensaje claro y un código HTTP
  4xx apropiado (400 para sintaxis inválida, 422 para validación de
  semántica), nunca procesándose de forma implícita.
- La validación MUST ejecutarse una sola vez en la capa de entrada; el
  resto del código puede asumir datos ya validados.

Rationale: validar en un único punto de entrada previene errores difíciles
de rastrear y garantiza respuestas consistentes ante entradas maliciosas
o malformadas.

### IV. Credenciales en Variables de Entorno (NO NEGOCIABLE)

Nunca se incluyen credenciales en el código:

- Contraseñas, tokens, claves de API y cualquier secreto MUST
  configurarse mediante variables de entorno; MUST NOT escribirse en el
  código, en el repositorio ni en archivos de configuración versionados.
- El código MUST fallar con un mensaje claro si falta una variable de
  entorno requerida, sin llegar a arrancar con valores por defecto
  inseguros.
- Cualquier secreto hardcodeado detectado en revisión MUST bloquear la
  fusión y, si llega a un commit, rotarse inmediatamente.

Rationale: los secretos en el repositorio se exponen a todo el que tenga
acceso (historial incluido) y su rotación es costosa y urgente.

### V. Manejo de Errores con Códigos HTTP Correctos

Los errores se comunican con mensajes claros y códigos HTTP correctos:

- Cada fallo MUST producir un mensaje claro y accionable (qué falló y
  cómo resolverlo), sin exponer detalles internos, stack traces ni datos
  sensibles al cliente.
- Se MUST usar el código HTTP que describe la situación real: 400/422
  (entrada inválida), 401/403 (autenticación/autorización), 404 (recurso
  inexistente), 409 (conflicto), 500 (error interno), 503 (servicio no
  disponible).
- El lado del servidor MUST registrar el detalle completo del error para
  su diagnóstico, separado del mensaje devuelto al cliente.

Rationale: los códigos HTTP correctos permiten que los clientes y
sistemas intermediarios reaccionen adecuadamente, y los mensajes claros
reducen el tiempo de diagnóstico.

### VI. Documentación y Comentarios en Español

Toda documentación y todos los comentarios se redactan en español:

- La documentación del proyecto (README, guías, especificaciones) y los
  comentarios de código MUST estar en español.
- Los comentarios MUST explicar el porqué de una decisión, no lo que hace
  el código obvio; se MUST eliminar todo comentario obsoleto.
- Los identificadores de código (nombres de variables, funciones, clases)
  MUST ser descriptivos; ante la duda entre un nombre en español o en
  inglés, se MUST mantener la coherencia con el resto del módulo.

Rationale: un idioma único en la documentación elimina ambigüedades y
reduce el coste de lectura para todo el equipo.

### VII. Solo Datos Ficticios en Pruebas

Las pruebas usan exclusivamente datos ficticios:

- Los tests MUST usar solo datos ficticios o generados; MUST NOT usar
  datos reales de producción, datos personales identificables ni
  credenciales reales.
- Los datos de prueba MUST vivir junto al test que los usa y ser
  deterministas: mismas entradas, mismos resultados.
- Cualquier dato real que se detecte en un test MUST reemplazarse por un
  equivalente ficticio antes de fusionar.

Rationale: los datos reales en pruebas exponen información sensible,
incumplen normativas de privacidad y hacen que los tests dependan de
entornos no reproducibles.

## Estándares de Calidad

- La puerta de calidad de cualquier cambio es: tests automatizados en
  verde, sin credenciales en el código, validación de entrada presente,
  manejo de errores con códigos HTTP correctos y documentación en
  español.
- Todo cambio MUST pasar las verificaciones automatizadas (tests,
  análisis estático si existe) antes de su fusión; un cambio con
  verificaciones en rojo MUST NOT fusionarse.
- La revisión de código MUST verificar el cumplimiento de los principios
  de esta constitución; la complejidad injustificada se rechaza en la
  revisión.

## Flujo de Desarrollo

- El trabajo se entrega en incrementos pequeños y verificables; cada
  incremento MUST incluir sus tests junto con el código que prueban
  (no tests diferidos a una tarea posterior).
- Definición de hecho (Done): funcionalidad implementada, validación de
  entrada incluida, errores manejados con códigos HTTP correctos, tests
  automatizados pasando, sin secretos y documentación en español
  actualizada.
- Antes de empezar código nuevo que afecte un contrato existente
  (endpoints, esquemas, respuestas de error), se MUST confirmar que los
  tests actuales siguen representando el comportamiento deseado.

## Governance

- Esta constitución suprema a cualquier práctica, convención o
  preferencia individual; los conflictos se resuelven a su favor.
- Enmiendas: cualquier cambio MUST proponerse por escrito, explicar su
  motivo y su impacto en proyectos existentes, aprobarse antes de
  aplicarse y registrarse actualizando versión y fechas en esta línea de
  versión.
- Política de versionado (SemVer de la gobernanza):
  - MAJOR: eliminación o redefinición incompatible de principios.
  - MINOR: nuevo principio o expansión material de su guía.
  - PATCH: aclaraciones, correcciones de redacción o de erratas.
- Revisión de cumplimiento: cada revisión de código o solicitud de
  fusión MUST comprobar el cumplimiento de esta constitución; las
  infracciones de los principios marcados como NO NEGOCIABLE bloquean la
  fusión.
- Responsables de gobernanza: los colaboradores del repositorio, mediante
  el proceso de enmienda descrito arriba; ninguna decisión externa a este
  proceso modifica la constitución.

**Version**: 1.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
