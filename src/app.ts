import express from "express";
import type { Express } from "express";
import { middlewareErrores } from "./errores";
import type { MensajesRepositorio } from "./repositorios/mensajes-repositorio";
import { crearRutasMensajes } from "./rutas/mensajes-ruta";
import { crearMensajesServicio } from "./servicios/mensajes-servicio";

/**
 * Crea la aplicación Express: parser JSON, rutas de mensajes y, el último,
 * el middleware de errores (así captura los fallos lanzados por las rutas).
 * `repositorio` permite inyectar un repositorio falso en los tests (D7);
 * si se omite, se usa el repositorio real de Supabase.
 */
export function crearApp(repositorio?: MensajesRepositorio): Express {
  const app = express();
  app.use(express.json());
  app.use(crearRutasMensajes(crearMensajesServicio(repositorio)));
  app.use(middlewareErrores);
  return app;
}
