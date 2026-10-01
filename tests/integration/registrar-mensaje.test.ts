import { describe, expect, it } from "vitest";
import request from "supertest";
import { crearApp } from "../../src/app";
import { crearRepositorioFalso } from "../apoyo/repositorio-falso";

// T019 — Test de integración: flujo completo con repositorio falso en memoria.
// Sin base de datos real y con datos ficticios (constitución VII).
describe("integración: registrar un mensaje", () => {
  it("el registro válido llega guardado al repositorio con id, fecha_hora y clasificación", async () => {
    const repositorio = crearRepositorioFalso();
    const app = crearApp(repositorio);

    const respuesta = await request(app).post("/mensajes").send({
      nombre: "Ana Prueba",
      dni: "12345678",
      telefono: "612345678",
      texto: "Quiero información del ciclo",
    });

    expect(respuesta.status).toBe(201);
    expect(repositorio.mensajes).toHaveLength(1);
    const guardado = repositorio.mensajes[0];
    expect(guardado).toMatchObject({
      id: respuesta.body.id,
      dni: "12345678",
      texto: "Quiero información del ciclo",
      clasificacion: "otro", // valor temporal de US1 (FR-009)
    });
    expect(Date.parse(guardado.fecha_hora)).not.toBeNaN();
  });

  it("el registro inválido no toca el repositorio", async () => {
    const repositorio = crearRepositorioFalso();
    const app = crearApp(repositorio);

    const respuesta = await request(app).post("/mensajes").send({
      nombre: "Ana Prueba",
      dni: "123", // inválido: no tiene 8 dígitos
      telefono: "612345678",
      texto: "Quiero información del ciclo",
    });

    expect(respuesta.status).toBe(400);
    expect(respuesta.body.campo).toBe("dni");
    expect(repositorio.mensajes).toHaveLength(0);
  });

  it("el duplicado dentro de la ventana no añade una segunda copia", async () => {
    const repositorio = crearRepositorioFalso();
    const app = crearApp(repositorio);
    const cuerpo = {
      nombre: "Ana Prueba",
      dni: "12345678",
      telefono: "612345678",
      texto: "Quiero información del ciclo",
    };

    expect((await request(app).post("/mensajes").send(cuerpo)).status).toBe(201);
    expect((await request(app).post("/mensajes").send(cuerpo)).status).toBe(409);
    expect(repositorio.mensajes).toHaveLength(1);
  });
});
