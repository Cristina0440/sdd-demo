import { describe, expect, it } from "vitest";
import { esquemaRegistro, normalizarTelefono } from "../../src/validacion/mensaje-esquema";

// T014 — Test unitario de normalización de teléfono (data-model.md):
// trim → elimina separadores (espacios y guiones) → elimina el prefijo
// peruano +51/51 → debe quedar un celular peruano de 9 dígitos que empieza
// por 9. Cualquier otro código de país (incluido +34) se rechaza.
const base = {
  nombre: "Ana Prueba",
  dni: "12345678",
  telefono: "987654321",
  texto: "Hola, buenas tardes",
};

describe("normalización de teléfono (celular peruano)", () => {
  it('convierte "+51 987 654 321" en "987654321" (válido)', () => {
    expect(normalizarTelefono("+51 987 654 321")).toBe("987654321");
    expect(esquemaRegistro.safeParse({ ...base, telefono: "+51 987 654 321" }).success).toBe(true);
  });

  it("acepta el prefijo +51 o 51 sin separadores y los separadores sin prefijo", () => {
    expect(normalizarTelefono("+51987654321")).toBe("987654321");
    expect(normalizarTelefono("51 987654321")).toBe("987654321");
    expect(normalizarTelefono("987 654 321")).toBe("987654321");
    expect(normalizarTelefono("987-654-321")).toBe("987654321");
    expect(esquemaRegistro.safeParse({ ...base, telefono: "987-654-321" }).success).toBe(true);
    expect(esquemaRegistro.safeParse({ ...base, telefono: "  987654321  " }).success).toBe(true);
  });

  it('rechaza cualquier otro código de país, incluido "+34" (España)', () => {
    for (const invalido of ["+34 612 345 678", "+34612345678", "+35161234567", "+1 555 123 4567"]) {
      expect(esquemaRegistro.safeParse({ ...base, telefono: invalido }).success).toBe(false);
    }
  });

  it("rechaza longitudes distintas de 9 y números que no empiezan por 9", () => {
    for (const invalido of ["98765432", "9876543210", "876543210", "612345678", "98765432X", ""]) {
      expect(esquemaRegistro.safeParse({ ...base, telefono: invalido }).success).toBe(false);
    }
  });
});
