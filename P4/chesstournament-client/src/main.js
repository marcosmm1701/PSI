import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

// Importamos el CSS de Bootstrap
import "./assets/main.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");

// Importa el archivo JavaScript de Bootstrap desde node_modules
import "../node_modules/bootstrap/dist/js/bootstrap.js";

// Importa el archivo CSS de Bootstrap desde node_modules
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
