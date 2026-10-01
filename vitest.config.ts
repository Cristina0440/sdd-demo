import { defineConfig } from "vitest/config";

// Configuración de vitest: entorno node y patrón de tests del proyecto.
// passWithNoTests deja `npm test` en verde durante la Fase 1, cuando aún no
// existe ningún archivo de test (punto de control de tasks.md).
export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    passWithNoTests: true,
  },
});
