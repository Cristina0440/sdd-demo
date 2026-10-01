import express from "express";
import type { Express } from "express";
import { middlewareErrores } from "./errores";

/**
 * Crea la aplicación Express: parser JSON y middleware de errores (T008).
 * Sin rutas aún: se registran en las fases de historias de usuario (T018, T026).
 */
export function crearApp(): Express {
  const app = express();
  app.use(express.json());
  app.use(middlewareErrores);
  return app;
}
