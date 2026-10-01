-- Esquema de la tabla `mensajes` para Supabase (PostgreSQL).
-- Ejecutar pegando este archivo en el SQL Editor de Supabase.
-- Solo estructura: sin datos reales (la semilla del quickstart usa datos ficticios).

create extension if not exists "pgcrypto";

create table if not exists mensajes (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  dni char(8) not null,
  telefono char(9) not null,
  texto text not null,
  fecha_hora timestamptz not null default now(),
  clasificacion text not null,
  -- Red de seguridad bajo la validación zod de la entrada (constitución III):
  -- cada regla de formato del data-model.md como restricción CHECK.
  constraint mensajes_dni_8_digitos check (dni ~ '^[0-9]{8}$'),
  constraint mensajes_telefono_9_digitos check (telefono ~ '^9[0-9]{8}$'),
  constraint mensajes_texto_no_vacio check (length(btrim(texto)) > 0),
  constraint mensajes_clasificacion_valida check (
    clasificacion in ('informacion_ciclo', 'devolucion', 'interes_inscripcion', 'otro')
  )
);

-- Seguridad a nivel de fila (RLS): habilitada SIN políticas. Sin políticas, el
-- acceso público (anon key) queda bloqueado por completo; el servicio se conecta
-- con la service role key, que salta (bypasea) el RLS, por lo que su lectura y
-- escritura no se ven afectadas.
alter table mensajes enable row level security;

-- Índice para la consulta de historial por DNI (SC-003: < 2 s con 10.000 mensajes).
create index if not exists mensajes_dni_fecha_hora_idx
  on mensajes (dni, fecha_hora desc);
