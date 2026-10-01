import { Router } from "express";
import type { Request, Response } from "express";
import type { MensajesServicio } from "../servicios/mensajes-servicio";

/**
 * Rutas de mensajes. La validación y la detección de duplicados las resuelve
 * el servicio (capa de entrada única, constitución III); los errores
 * (400/409/500) los mapea el middleware de errores de `src/errores.ts`.
 */
export function crearRutasMensajes(servicio: MensajesServicio): Router {
  const ruta = Router();

  // POST /mensajes → 201 con el mensaje registrado (contrato de la API).
  ruta.post("/mensajes", async (req: Request, res: Response) => {
    const mensaje = await servicio.registrar(req.body);
    res.status(201).json(mensaje);
  });

  return ruta;
}
