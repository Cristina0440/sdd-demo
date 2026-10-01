import { z } from "zod";

/**
 * Normaliza un teléfono (data-model.md): trim → elimina los separadores
 * (espacios y guiones) → elimina el prefijo peruano `+51` o `51` si existe.
 * Después solo debe quedar un celular peruano: `^9[0-9]{8}$`. Cualquier otro
 * código de país (incluido `+34`) no se elimina y por tanto se rechaza.
 */
export function normalizarTelefono(telefono: string): string {
  const sinSeparadores = telefono.trim().replace(/[\s-]+/g, "");
  return sinSeparadores.replace(/^\+?51/, "");
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
  // FR-003: celular peruano, exactamente 9 dígitos que empiezan por 9.
  telefono: z
    .string()
    .transform(normalizarTelefono)
    .pipe(z.string().regex(/^9[0-9]{8}$/, "El teléfono debe tener exactamente 9 dígitos y empezar por 9")),
  // FR-004: no vacío ni solo espacios, pero se conserva tal cual llegó
  // (por eso se usa `refine` y no `trim`: el historial guarda el texto original).
  texto: z.string().refine((valor) => valor.trim().length > 0, "El texto no puede estar vacío"),
});
