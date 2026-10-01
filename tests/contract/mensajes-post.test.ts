import { describe, expect, it } from "vitest";
import request from "supertest";
import { crearApp } from "../../src/app";
import { crearRepositorioFalso } from "../apoyo/repositorio-falso";

// T010 — Test de contrato: POST /mensajes con body válido → 201.
// El texto "Hola, buenas tardes" no contiene palabras clave, de modo que la
// expectativa `clasificacion: "otro"` sigue siendo válida tras US3 (FR-009).
describe("POST /mensajes — contrato de registro válido", () => {
  it("responde 201 con id, fecha_hora y clasificacion 'otro', y guarda el mensaje", async () => {
    const repositorio = crearRepositorioFalso();
    const app = crearApp(repositorio);

    const respuesta = await request(app).post("/mensajes").send({
      nombre: "Ana Prueba",
      dni: "12345678",
      telefono: "987654321",
      texto: "Hola, buenas tardes",
    });

    expect(respuesta.status).toBe(201);
    expect(respuesta.body.id).toBeTruthy();
    expect(respuesta.body.fecha_hora).toBeTruthy();
    expect(respuesta.body.clasificacion).toBe("otro");
    expect(respuesta.body).toMatchObject({
      nombre: "Ana Prueba",
      dni: "12345678",
      telefono: "987654321",
      texto: "Hola, buenas tardes",
    });
    expect(repositorio.mensajes).toHaveLength(1);
  });
});
