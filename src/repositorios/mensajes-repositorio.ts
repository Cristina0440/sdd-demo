import { createClient } from "@supabase/supabase-js";
import type { SupabaseClient } from "@supabase/supabase-js";
import { obtenerEntorno } from "../config/entorno";

/** Mensaje tal y como se persiste y se devuelve en la API (contrato). */
export interface Mensaje {
  id: string;
  nombre: string;
  dni: string;
  telefono: string;
  texto: string;
  fecha_hora: string;
  clasificacion: string;
}

/** Operaciones que el servicio necesita sobre la tabla `mensajes`. */
export interface MensajesRepositorio {
  insertar(mensaje: Mensaje): Promise<void>;
  buscarReciente(dni: string, texto: string, ventanaSegundos: number): Promise<Mensaje | null>;
}

// Cliente único de Supabase, creado perezosamente con la service role key del
// entorno ya validado en el arranque (constitución IV, research D5).
let cliente: SupabaseClient | null = null;

function obtenerCliente(): SupabaseClient {
  if (cliente === null) {
    const entorno = obtenerEntorno();
    cliente = createClient(entorno.supabaseUrl, entorno.supabaseServiceRoleKey);
  }
  return cliente;
}

/** Repositorio real contra Supabase (única tabla `mensajes`). */
export function crearRepositorioSupabase(): MensajesRepositorio {
  return {
    async insertar(mensaje: Mensaje): Promise<void> {
      const { error } = await obtenerCliente().from("mensajes").insert(mensaje);
      if (error !== null) {
        throw new Error(`No se pudo guardar el mensaje: ${error.message}`);
      }
    },

    async buscarReciente(dni: string, texto: string, ventanaSegundos: number): Promise<Mensaje | null> {
      // Misma regla que el data-model: mismo dni y mismo texto (ya recortado
      // por el servicio) con fecha_hora dentro de la ventana (FR-016, D2).
      const desde = new Date(Date.now() - ventanaSegundos * 1000).toISOString();
      const { data, error } = await obtenerCliente()
        .from("mensajes")
        .select("*")
        .eq("dni", dni)
        .eq("texto", texto)
        .gt("fecha_hora", desde)
        .limit(1);

      if (error !== null) {
        throw new Error(`No se pudo consultar el mensaje duplicado: ${error.message}`);
      }

      const filas = data as Mensaje[];
      return filas.length > 0 ? filas[0] : null;
    },
  };
}
