// Archivo creado para contar el numero de personas almacenadas.

import { defineStore } from "pinia";

const COUNTER_LOCAL_STORAGE_KEY = "localCounter";

const getCount = () => {
  const storedCounter = localStorage.getItem(COUNTER_LOCAL_STORAGE_KEY);
  return storedCounter ? JSON.parse(storedCounter) : 0;
};
export const useCounterStore = defineStore("counter", {
  state: () => ({
    count: getCount(),
  }),
  getters: {
    singleCount(state) {
      return state.count;
    },
  },
  actions: {
    increment() {
      this.count++;
      localStorage.setItem(
        COUNTER_LOCAL_STORAGE_KEY,
        JSON.stringify(this.count)
      );
    },
  },
});
if (localStorage.getItem("state")) {
  pinia.state.value = JSON.parse(localStorage.getItem("state"));
}
