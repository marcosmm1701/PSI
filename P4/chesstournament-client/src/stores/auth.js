// Fichero para manejar la autenticación de los usuarios
// y el almacenamiento del token JWT en el cliente

import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    isAuthenticated: false,
  }),
  actions: {
    setToken(newToken) {
      this.isAuthenticated = true;
      this.token = newToken;
    },
    logout() {
      this.isAuthenticated = false;
      this.token = null;
    },
  },
});
