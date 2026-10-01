import { describe, expect, it } from "vitest";
import request from "supertest";
import { crearApp } from "../../src/app";
import { crearRepositorioFalso } from "../apoyo/repositorio-falso";

// T012 — Test de contrato: misma ventana de duplicados de 10 segundos (FR-016,
// decisión D1): mismo dni + mismo texto (tras trim) dentro de la ventana → 409
// y nada guardado; pasado el tiempo → 201 como mensaje nuevo.
describe("POST /mensajes — contrato de duplicados (ventana de 10 s)", () => {
  it("devuelve 409 dentro de la ventana y 201 fuera de ella", async () => {
    const repositorio = crearRepositorioFalso();
    const app = crearApp(repositorio);
    const cuerpo = {
      nombre: "Ana Prueba",
      dni: "12345678",
      telefono: "987654321",
      texto: "Quiero información del ciclo",
    };

    const primera = await request(app).post("/mensajes").send(cuerpo);
    expect(primera.status).toBe(201);
    expect(repositorio.mensajes).toHaveLength(1);

    const duplicada = await request(app).post("/mensajes").send(cuerpo);
    expect(duplicada.status).toBe(409);
    expect(duplicada.body.mensaje).toContain("duplicado");
    expect(repositorio.mensajes).toHaveLength(1); // no se guardó la copia

    // Pasados los 10 s, el mismo texto es un mensaje nuevo.
    repositorio.envejecerMensajes(11);
    const pasadaLaVentana = await request(app).post("/mensajes").send(cuerpo);
    expect(pasadaLaVentana.status).toBe(201);
    expect(repositorio.mensajes).toHaveLength(2);
  });
});
