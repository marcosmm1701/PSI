<!-- FormularioPersona.vue -->
<template>
  <!-- Contenedor principal del componente -->
  <div id="formulario-persona">
    <!-- Formulario con campos para ingresar informacion de una persona -->
    <form @submit.prevent="enviarFormulario">
      <div class="container">
        <!-- Primera fila con campos de nombre, apellido y email -->
        <div class="row">
          <div class="col-md-4">
            <div class="form-group">
              <!-- Etiqueta y campo de entrada para el nombre -->
              <label>Nombre</label>
              <!-- ref: la referencia al elemento input con nombre 'nombre' -->
              <!-- v-model: Vinculacion bidireccional con la propiedad 'nombre' de la variable reactiva 'persona' -->
              <!-- type: tipo de campo de entrada -->
              <!-- class: Clase de Bootstrap para estilos de formulario -->
              <!-- data-cy: Atributo de datos para seleccion en pruebas automatizadas (Cypress). Haremos uso del mismo mas adelante -->
              <!-- :class:  condicional que se aplica si 'procesando' es verdadero y 'nombreInvalido' es verdadero -->
              <!-- @focus: Manejador de evento cuando el input obtiene el foco -->
              <!-- @keypress: Manejador de evento cuando se presiona una tecla en el input -->
              <input
                ref="nombre"
                v-model="persona.nombre"
                type="text"
                class="form-control"
                data-cy="name"
                :class="{ 'is-invalid': procesando && nombreInvalido }"
                @focus="resetEstado"
                @keypress="resetEstado"
              />
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-group">
              <!-- Etiqueta y campo de entrada para el apellido -->
              <label>Apellido</label>
              <input
                v-model="persona.apellido"
                type="text"
                class="form-control"
                data-cy="surname"
                :class="{ 'is-invalid': procesando && apellidoInvalido }"
                @focus="resetEstado"
              />
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-group">
              <!-- Etiqueta y campo de entrada para el correo electronico -->
              <label>Email</label>
              <input
                v-model="persona.email"
                type="email"
                class="form-control"
                data-cy="email"
                :class="{ 'is-invalid': procesando && emailInvalido }"
                @focus="resetEstado"
              />
            </div>
          </div>
        </div>
        <br />
        <!-- Segunda fila con un boton para agregar persona -->
        <div class="row">
          <div class="col-md-4">
            <div class="form-group">
              <!-- Boton para agnadir persona -->
              <button class="btn btn-primary" data-cy="add-button">
                Agnadir persona
              </button>
            </div>
          </div>
        </div>
      </div>
      <br />
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div
              v-if="error && procesando"
              class="alert alert-danger"
              role="alert"
            >
              Debes rellenar todos los campos!
            </div>
            <div v-if="correcto" class="alert alert-success" role="alert">
              La persona ha sido agregada correctamente!
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
// Importacion de la funcion "ref" y "computed" de Vue 3
import { ref, computed } from "vue";

// definicion del componente
defineOptions({
  // nombre del componente
  name: "FormularioPersona",
});

// Declaracion de una variable reactiva "persona" con propiedades nombre, apellido y email
const persona = ref({
  nombre: "",
  apellido: "",
  email: "",
});

// Importacion de la funcion "defineEmits" de Vue 3
const emit = defineEmits(["add-persona"]);

const nombre = ref(null);

// Funcion para enviar el formulario
const enviarFormulario = () => {
  procesando.value = true;
  resetEstado();

  // Comprobamos la presencia de errores
  if (nombreInvalido.value || apellidoInvalido.value || emailInvalido.value) {
    error.value = true;
    return;
  }

  // Emitimos el evento y esperamos respuesta de App.vue
  emit("add-persona", persona.value, (errorMessage) => {
    if (errorMessage) {
      error.value = true;
      alert(errorMessage); // Mostrar el error recibido
    } else {
      correcto.value = true;
    }
  });

  // Enfocar el campo de nombre. Es decir, el cursor, al recargar la pagina se enfocara en el campo de nombre
  nombre.value.focus();

  if (!error.value) {
    // Limpiamos el formulario
    persona.value = {
      nombre: "",
      apellido: "",
      email: "",
    };
  }

  procesando.value = false;
};

// Computed properties para validar campos del formulario. Comprobamos si el campo esta vacio
const nombreInvalido = computed(() => persona.value.nombre.length < 1);
const apellidoInvalido = computed(() => persona.value.apellido.length < 1);
const emailInvalido = computed(() => persona.value.email.length < 1);

// Variables reactivas para mostrar mensajes de estado
const procesando = ref(false);
const correcto = ref(false);
const error = ref(false);

const resetEstado = () => {
  correcto.value = false;
  error.value = false;
};
</script>

<style scoped>
/* Estilos especificos del componente con el modificador "scoped" */
form {
  margin-bottom: 2rem;
}
</style>
