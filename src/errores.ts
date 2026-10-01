import type { NextFunction, Request, Response } from "express";
import { ZodError } from "zod";

/**
 * Error con el código HTTP que corresponde responder al cliente (constitución V).
 * `campo` es opcional: solo se incluye cuando el fallo está en un campo concreto
 * de la entrada (p. ej. `{ campo: "dni", mensaje: ... }`).
 */
export class AppError extends Error {
  constructor(
    public readonly codigoHttp: number,
    mensaje: string,
    public readonly campo?: string,
  ) {
    super(mensaje);
    this.name = "AppError";
  }
}

/**
 * Middleware de errores de Express (los 4 parámetros hacen que Express lo
 * reconozca; `_next` es obligatorio en la firma aunque no se use).
 *
 * - 400: validación fallida (ZodError o cuerpo JSON malformado) → nada persistido.
 * - 409: duplicado, cuando el servicio lanza `AppError(409, ...)`.
 * - 500: cualquier otro fallo → mensaje genérico al cliente y detalle completo
 *   solo en el log del servidor; nunca stack traces al cliente (constitución V).
 */
export function middlewareErrores(
  err: unknown,
  req: Request,
  res: Response,
  _next: NextFunction,
): void {
  // Error previsto de negocio: su código y su mensaje claro.
  if (err instanceof AppError) {
    console.warn(`${req.method} ${req.originalUrl} → ${err.codigoHttp}: ${err.message}`);
    if (err.campo !== undefined) {
      res.status(err.codigoHttp).json({ campo: err.campo, mensaje: err.message });
    } else {
      res.status(err.codigoHttp).json({ mensaje: err.message });
    }
    return;
  }

  // Validación zod: se informa el primer campo fallido (orden del esquema).
  if (err instanceof ZodError) {
    const primerError = err.issues[0];
    const campo = primerError?.path.join(".");
    res.status(400).json({
      campo: campo === "" || campo === undefined ? undefined : campo,
      mensaje: primerError?.message ?? "Datos de entrada inválidos",
    });
    return;
  }

  // Cuerpo que ni siquiera es JSON válido (parser de Express) → 400, no 500.
  if (err instanceof SyntaxError && "status" in err && typeof err.status === "number") {
    res.status(400).json({ mensaje: "El cuerpo de la petición no es JSON válido" });
    return;
  }

  // Fallo inesperado: detalle completo solo en el log del servidor.
  console.error(`${req.method} ${req.originalUrl} → 500`, err);
  res.status(500).json({ mensaje: "Error interno del servidor" });
}
