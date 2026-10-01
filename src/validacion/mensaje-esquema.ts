import { z } from "zod";

/**
 * Normaliza un teléfono (data-model.md): trim → elimina el prefijo `+34` si
 * existe → elimina los espacios. Después solo debe quedar `^[0-9]{9}$`.
 */
export function normalizarTelefono(telefono: string): string {
  const recortado = telefono.trim();
  const sinPrefijo = recortado.startsWith("+34") ? recortado.slice(3) : recortado;
  return sinPrefijo.replace(/\s+/g, "");
}

/**
 * Esquema zod del body de `POST /mensajes` (T015).
 * Es la validación única de la entrada (constitución III): cualquier fallo se
 * rechaza antes de persistir nada (FR-012) y el orden de los campos es el que
 * exige el contrato para informar el primero que falla.
 */
export const esquemaRegistro = z.object({
  // FR-017: obligatorio y no vacío tras trim (el valor se guarda recortado).
  nombre: z.string().trim().min(1, "El nombre no puede estar vacío"),
  // FR-002: exactamente 8 dígitos numéricos.
  dni: z.string().trim().regex(/^[0-9]{8}$/, "El DNI debe tener exactamente 8 dígitos"),
  // FR-003: se normaliza y el resultado debe ser exactamente 9 dígitos.
  telefono: z
    .string()
    .transform(normalizarTelefono)
    .pipe(z.string().regex(/^[0-9]{9}$/, "El teléfono debe tener exactamente 9 dígitos")),
  // FR-004: no vacío ni solo espacios, pero se conserva tal cual llegó
  // (por eso se usa `refine` y no `trim`: el historial guarda el texto original).
  texto: z.string().refine((valor) => valor.trim().length > 0, "El texto no puede estar vacío"),
});
