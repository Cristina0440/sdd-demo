import { config } from "dotenv";
import { z } from "zod";

// Variables de entorno obligatorias del servicio (constitución IV): nunca
// llevan valores por defecto inseguros ni secretos en el repositorio.
const esquemaEntorno = z.object({
  SUPABASE_URL: z.string().trim().min(1, "SUPABASE_URL está vacía"),
  SUPABASE_SERVICE_ROLE_KEY: z.string().trim().min(1, "SUPABASE_SERVICE_ROLE_KEY está vacía"),
});

export interface Entorno {
  supabaseUrl: string;
  supabaseServiceRoleKey: string;
}

// Último entorno validado, para que el repositorio acceda a las claves sin
// pasarlas por todas las capas (el arranque las valida una sola vez).
let entornoCargado: Entorno | null = null;

/**
 * Carga `.env` y valida las variables obligatorias con zod.
 * Si falta alguna, lanza un Error con un mensaje claro que indica la variable
 * que falta: el arranque falla sin llegar a escuchar (constitución IV).
 */
export function cargarEntorno(): Entorno {
  config();

  const resultado = esquemaEntorno.safeParse(process.env);
  if (!resultado.success) {
    const faltantes = resultado.error.issues.map((issue) => issue.path.join(".")).join(", ");
    throw new Error(
      `Variables de entorno obligatorias ausentes o vacías: ${faltantes}. ` +
        "Copia .env.example a .env y rellénalas antes de arrancar.",
    );
  }

  entornoCargado = {
    supabaseUrl: resultado.data.SUPABASE_URL,
    supabaseServiceRoleKey: resultado.data.SUPABASE_SERVICE_ROLE_KEY,
  };
  return entornoCargado;
}

/** Devuelve el entorno ya validado por `cargarEntorno` (error claro si aún no se cargó). */
export function obtenerEntorno(): Entorno {
  if (entornoCargado === null) {
    throw new Error("El entorno todavía no se ha cargado: llama a cargarEntorno() al arrancar.");
  }
  return entornoCargado;
}
