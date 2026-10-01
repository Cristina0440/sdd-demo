import { randomUUID } from "node:crypto";
import { AppError } from "../errores";
import {
  crearRepositorioSupabase,
  type Mensaje,
  type MensajesRepositorio,
} from "../repositorios/mensajes-repositorio";
import { esquemaRegistro } from "../validacion/mensaje-esquema";

/** Ventana de detección de duplicados en segundos (FR-016, decisión D1). */
export const VENTANA_DUPLICADOS_SEGUNDOS = 10;

export interface MensajesServicio {
  /** Registra un mensaje: valida, descarta duplicados y persiste (FR-016). */
  registrar(datos: unknown): Promise<Mensaje>;
}

/**
 * Crea el servicio de mensajes. Por defecto usa el repositorio de Supabase;
 * los tests inyectan un repositorio falso en memoria (research D7).
 */
export function crearMensajesServicio(
  repositorio: MensajesRepositorio = crearRepositorioSupabase(),
): MensajesServicio {
  return {
    async registrar(datos: unknown): Promise<Mensaje> {
      // Validación única de la entrada (constitución III): si falla, ZodError
      // llega al middleware y responde 400 sin tocar el repositorio (FR-012).
      const validados = esquemaRegistro.parse(datos);

      // Anti-duplicados: mismo dni + mismo texto (tras trim) dentro de la
      // ventana de 10 s → 409 y no se guarda nada (FR-016, decisión D2).
      const duplicado = await repositorio.buscarReciente(
        validados.dni,
        validados.texto.trim(),
        VENTANA_DUPLICADOS_SEGUNDOS,
      );
      if (duplicado !== null) {
        throw new AppError(
          409,
          "Mensaje duplicado: idéntico a uno registrado en los últimos 10 segundos",
        );
      }

      const mensaje: Mensaje = {
        id: randomUUID(),
        nombre: validados.nombre,
        dni: validados.dni,
        telefono: validados.telefono,
        texto: validados.texto, // se conserva tal cual llegó (data-model.md)
        fecha_hora: new Date().toISOString(),
        clasificacion: "otro", // temporal hasta que US3 instale el clasificador (FR-009)
      };

      await repositorio.insertar(mensaje);
      return mensaje;
    },
  };
}
