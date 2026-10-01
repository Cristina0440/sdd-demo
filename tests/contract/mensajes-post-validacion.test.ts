import { describe, expect, it } from "vitest";
import request from "supertest";
import { crearApp } from "../../src/app";
import { crearRepositorioFalso } from "../apoyo/repositorio-falso";

// T011 — Test de contrato: cada regla de validación (FR-002/003/004/017)
// responde 400 con el campo y el repositorio NUNCA recibe `insertar` (FR-012).
interface CasioInvalido {
  titulo: string;
  campo: string;
  cuerpo: Record<string, string>;
}

const casosInvalidos: CasioInvalido[] = [
  {
    titulo: "nombre vacío",
    campo: "nombre",
    cuerpo: { nombre: "", dni: "12345678", telefono: "987654321", texto: "Hola, buenas tardes" },
  },
  {
    titulo: 'dni "12345" (no tiene 8 dígitos)',
    campo: "dni",
    cuerpo: { nombre: "Ana Prueba", dni: "12345", telefono: "987654321", texto: "Hola, buenas tardes" },
  },
  {
    titulo: 'telefono "98765432X" (no son 9 dígitos)',
    campo: "telefono",
    cuerpo: { nombre: "Ana Prueba", dni: "12345678", telefono: "98765432X", texto: "Hola, buenas tardes" },
  },
  {
    titulo: 'texto "   " (solo espacios)',
    campo: "texto",
    cuerpo: { nombre: "Ana Prueba", dni: "12345678", telefono: "987654321", texto: "   " },
  },
];

describe("POST /mensajes — contrato de validación", () => {
  it.each(casosInvalidos)(
    "rechaza $titulo con 400 y campo $campo, sin persistir nada",
    async ({ campo, cuerpo }) => {
      const repositorio = crearRepositorioFalso();
      const app = crearApp(repositorio);

      const respuesta = await request(app).post("/mensajes").send(cuerpo);

      expect(respuesta.status).toBe(400);
      expect(respuesta.body.campo).toBe(campo);
      expect(typeof respuesta.body.mensaje).toBe("string");
      expect(respuesta.body.mensaje).not.toBe("");
      // FR-012: nada llega a guardarse.
      expect(repositorio.mensajes).toHaveLength(0);
    },
  );
});
