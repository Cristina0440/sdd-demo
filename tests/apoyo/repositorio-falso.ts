import type { Mensaje, MensajesRepositorio } from "../../src/repositorios/mensajes-repositorio";

/**
 * Repositorio falso en memoria: sustituye a Supabase en los tests para que
 * `npm test` funcione sin base de datos real (research D7) y con solo datos
 * ficticios (constitución VII).
 */
export interface RepositorioFalso extends MensajesRepositorio {
  /** Mensajes guardados, para que los tests puedan inspeccionar el estado. */
  mensajes: Mensaje[];
  /** Envejece todos los mensajes guardados para salir de la ventana de 10 s. */
  envejecerMensajes(segundos: number): void;
}

export function crearRepositorioFalso(): RepositorioFalso {
  const mensajes: Mensaje[] = [];

  return {
    mensajes,

    async insertar(mensaje: Mensaje): Promise<void> {
      mensajes.push({ ...mensaje });
    },

    async buscarReciente(dni: string, texto: string, ventanaSegundos: number): Promise<Mensaje | null> {
      const limite = Date.now() - ventanaSegundos * 1000;
      const encontrado = mensajes.find(
        (mensaje) =>
          mensaje.dni === dni &&
          mensaje.texto.trim() === texto &&
          Date.parse(mensaje.fecha_hora) > limite,
      );
      return encontrado ? { ...encontrado } : null;
    },

    envejecerMensajes(segundos: number): void {
      for (const mensaje of mensajes) {
        mensaje.fecha_hora = new Date(Date.parse(mensaje.fecha_hora) - segundos * 1000).toISOString();
      }
    },
  };
}
