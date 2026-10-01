import { describe, expect, it } from "vitest";
import { esquemaRegistro, normalizarTelefono } from "../../src/validacion/mensaje-esquema";

// T014 — Test unitario de normalización de teléfono (data-model.md):
// trim → elimina el prefijo +34 si existe → elimina espacios → 9 dígitos.
const base = {
  nombre: "Ana Prueba",
  dni: "12345678",
  telefono: "612345678",
  texto: "Hola, buenas tardes",
};

describe("normalización de teléfono", () => {
  it('convierte "+34 612 345 678" en "612345678" (válido)', () => {
    expect(normalizarTelefono("+34 612 345 678")).toBe("612345678");
    expect(esquemaRegistro.safeParse({ ...base, telefono: "+34 612 345 678" }).success).toBe(true);
  });

  it('rechaza "+35161234567": solo se elimina el prefijo +34', () => {
    expect(normalizarTelefono("+35161234567")).toBe("+35161234567");
    expect(esquemaRegistro.safeParse({ ...base, telefono: "+35161234567" }).success).toBe(false);
  });

  it("quita espacios internos y el trim inicial", () => {
    expect(normalizarTelefono("  612 345 678  ")).toBe("612345678");
    expect(normalizarTelefono("+34612345678")).toBe("612345678");
  });
});
