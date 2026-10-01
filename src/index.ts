import { crearApp } from "./app";
import { cargarEntorno } from "./config/entorno";

const PUERTO = Number(process.env.PORT ?? 3000);

function iniciar(): void {
  // Sin variables de entorno válidas no se arranca (constitución IV):
  // mensaje claro que indica la variable que falta y salida con error.
  try {
    cargarEntorno();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  const app = crearApp();
  app.listen(PUERTO, () => {
    console.log(`Servidor escuchando en http://localhost:${PUERTO}`);
  });
}

iniciar();
