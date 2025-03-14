import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  define: {
    // Configuramos las feature flags de Vue. Esto lo hemos hecho para evitar un error de la consola
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
    __VUE_OPTIONS_API__: true, // Habilita la API de opciones (Options API)
    __VUE_PROD_DEVTOOLS__: false, // Deshabilita Vue DevTools en producción
  },
});
