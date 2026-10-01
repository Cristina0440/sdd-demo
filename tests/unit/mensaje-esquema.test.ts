import { describe, expect, it } from "vitest";
import { esquemaRegistro } from "../../src/validacion/mensaje-esquema";

// T013 — Test unitario del esquema zod de registro: las reglas exactas de
// spec.md/FR (nombre no vacío tras trim, DNI ^[0-9]{8}$, teléfono ^[0-9]{9}$
// tras normalizar, texto no vacío ni solo espacios).
const base = {
  nombre: "Ana Prueba",
  dni: "12345678",
  telefono: "612345678",
  texto: "Hola, buenas tardes",
};

describe("esquema de registro (zod)", () => {
  it("acepta un registro válido con todos los campos", () => {
    expect(esquemaRegistro.safeParse(base).success).toBe(true);
  });

  it("nombre: obligatorio y no vacío tras trim", () => {
    expect(esquemaRegistro.safeParse({ ...base, nombre: "   " }).success).toBe(false);
    expect(esquemaRegistro.safeParse({ ...base, nombre: "" }).success).toBe(false);
    expect(esquemaRegistro.safeParse({ dni: base.dni, telefono: base.telefono, texto: base.texto }).success).toBe(
      false,
    );
    const conEspacios = esquemaRegistro.safeParse({ ...base, nombre: "  Ana  " });
    expect(conEspacios.success && conEspacios.data.nombre).toBe("Ana");
  });

  it("dni: exactamente 8 dígitos numéricos ^[0-9]{8}$", () => {
    for (const invalido of ["12345", "123456789", "1234567a", "12 45678", ""]) {
      expect(esquemaRegistro.safeParse({ ...base, dni: invalido }).success).toBe(false);
    }
    const fallo = esquemaRegistro.safeParse({ ...base, dni: "12345" });
    expect(fallo.success).toBe(false);
    expect(fallo.error?.issues[0].message).toBe("El DNI debe tener exactamente 8 dígitos");
  });

  it("telefono: exactamente 9 dígitos numéricos ^[0-9]{9}$ tras normalizar", () => {
    expect(esquemaRegistro.safeParse({ ...base, telefono: "+34 612 345 678" }).success).toBe(true);
    expect(esquemaRegistro.safeParse({ ...base, telefono: "612 345 678" }).success).toBe(true);
    for (const invalido of ["61234567", "61234567890", "61234567X", ""]) {
      expect(esquemaRegistro.safeParse({ ...base, telefono: invalido }).success).toBe(false);
    }
    const fallo = esquemaRegistro.safeParse({ ...base, telefono: "61234567" });
    expect(fallo.success).toBe(false);
    expect(fallo.error?.issues[0].message).toBe("El teléfono debe tener exactamente 9 dígitos");
  });

  it("texto: no vacío ni solo espacios en blanco, y se conserva tal cual llegó", () => {
    expect(esquemaRegistro.safeParse({ ...base, texto: "" }).success).toBe(false);
    expect(esquemaRegistro.safeParse({ ...base, texto: "   " }).success).toBe(false);
    expect(esquemaRegistro.safeParse({ ...base, texto: "\t\n " }).success).toBe(false);
    const conEspacios = esquemaRegistro.safeParse({ ...base, texto: "  Hola  " });
    expect(conEspacios.success).toBe(true);
    // data-model.md: el texto se valida con trim pero NO se recorta.
    expect(conEspacios.success && conEspacios.data.texto).toBe("  Hola  ");
  });
});
