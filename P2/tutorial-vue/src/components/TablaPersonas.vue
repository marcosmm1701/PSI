<!-- src/components/TablaPersonas.vue -->

<template>
  <!-- Contenedor principal del componente -->
  <div id="tabla-personas">
    <div v-if="!personas.length" class="alert alert-info" role="alert">
      No se han encontrado personas
    </div>

    <div v-else>
      <!-- Tabla para mostrar informacion de personas -->
      <table class="table">
        <!-- Encabezado de la tabla -->
        <thead>
          <!-- nombres de columnas -->
          <tr>
            <th>Nombre</th>
            <th>Apellido</th>
            <th>Email</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <!-- Cuerpo de la tabla con datos dinamicos -->
        <tbody>
          <!-- Iteracion sobre el array de personas utilizando v-for -->
          <tr v-for="persona in personas" :key="persona.id">
            <td v-if="editando === persona.id">
              <input
                id="persona.nombre"
                v-model="persona.nombre"
                type="text"
                class="form-control"
                data-cy="persona-nombre"
              />
            </td>
            <!-- Celda de datos para el nombre de la persona -->
            <td v-else>
              {{ persona.nombre }}
            </td>

            <!-- Celda de datos para el apellido de la persona -->
            <td v-if="editando === persona.id">
              <input
                v-model="persona.apellido"
                type="text"
                class="form-control"
              />
            </td>
            <td v-else>
              {{ persona.apellido }}
            </td>

            <!-- Celda de datos para el correo electronico de la persona -->
            <td v-if="editando === persona.id">
              <input
                v-model="persona.email"
                type="email"
                class="form-control"
              />
            </td>
            <td v-else>
              {{ persona.email }}
            </td>

            <td v-if="editando === persona.id">
              <div class="acciones">
                <button
                  class="btn btn-success"
                  data-cy="save-button"
                  @click="guardarPersona(persona)"
                >
                  💾 Guardar
                </button>
                <button
                  class="btn btn-secondary ml-2"
                  data-cy="cancel-button"
                  @click="cancelarEdicion(persona)"
                >
                  ❌ Cancelar
                </button>
              </div>
            </td>

            <td v-else>
              <div class="acciones">
                <button
                  class="btn btn-danger ml-2"
                  data-cy="delete-button"
                  @click="$emit('delete-persona', persona.id)"
                >
                  &#x1F5D1; Eliminar
                </button>

                <button
                  class="btn btn-info"
                  data-cy="edit-button"
                  @click="editarPersona(persona)"
                >
                  &#x1F58A;Editar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// definicion del componente
defineOptions({
  // nombre del componente
  name: "TablaPersonas",
});

// declaramos y damos valor por defecto para la propiedad personas
// lo eliminamos por el lint

const { personas } = defineProps({
  personas: {
    type: Array,
    default: () => [],
  },
});

const editando = ref(null); // ID de la persona que está siendo editada
const personaEditada = ref(null); // Copia de los datos originales de la persona

const editarPersona = (persona) => {
  personaEditada.value = { ...persona }; // Guarda una copia antes de editar
  editando.value = persona.id; // Establece el ID de la persona que está siendo editada
};

const emit = defineEmits(["actualizar-persona", "delete-persona"]);

const guardarPersona = (persona) => {
  if (
    !persona.nombre.length ||
    !persona.apellido.length ||
    !persona.email.length
  ) {
    return;
  }
  emit("actualizar-persona", persona.id, persona);
  editando.value = null;
};

const cancelarEdicion = (persona) => {
  Object.assign(persona, personaEditada.value);
  editando.value = null;
};
</script>

<style scoped>
/* Estilos especificos del componente con el modificador "scoped" */
.acciones {
  display: flex;
  gap: 10px;
  /* Espacio entre botones */
}

button {
  font-family: "Segoe UI Emoji", "Noto Emoji", sans-serif;
}
</style>
