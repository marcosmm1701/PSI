<!-- App.vue -->
<template>
  <div id="app" class="container">
    <div class="row">
      <div class="col-md-12">
        <h1>Personas</h1>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <!-- Formulario para agregar nuevas personas -->
        <formulario-persona @add-persona="agregarPersona" />
        <!-- Inclusion del componente "FormularioPersona" -->

        <!-- Inclusion del componente "TablaPersonas" -->
        <tabla-personas
          :personas="personas"
          @delete-persona="eliminarPersona"
          @actualizar-persona="actualizarPersona"
        />
      </div>
    </div>
  </div>
  <div>
    <p>Count is {{ store.count }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useCounterStore } from "@/stores/counter";

// Importacion del componente "FormularioPersona"
import FormularioPersona from "@/components/FormularioPersona.vue";
// Importacion del componente "TablaPersonas"
import TablaPersonas from "@/components/TablaPersonas.vue";

// Definicion del componente Vue
defineOptions({
  // Nombre del componente
  name: "App",
});

// Declaracion de una variable reactiva "personas" usando "ref"
const personas = ref([]);
const store = useCounterStore();

// Obtenemos la URL del backend desde las variables de entorno
const API_URL = import.meta.env.VITE_DJANGOURL;
console.log("API_URL:", API_URL);

const listadoPersonas = async () => {
  // Metodo para obtener un listado de personas
  try {
    const response = await fetch(API_URL);
    personas.value = await response.json();
  } catch (error) {
    console.error(error);
  }
};

const agregarPersona = async (persona, callback) => {
  try {
    // Validamos que el email tiene un formato correcto antes de hacer la petición
    if (!persona.email.includes("@") || !persona.email.includes(".")) {
      alert("Por favor, introduce un email válido.");
      callback(false); // Indica que hubo un error
      return;
    }

    const response = await fetch(API_URL, {
      method: "POST",
      body: JSON.stringify(persona),
      headers: { "Content-type": "application/json; charset=UTF-8" },
    });

    const personaCreada = await response.json();

    if (!response.ok) {
      console.error("Error al agregar persona:", personaCreada);
      alert(personaCreada.email ? personaCreada.email[0] : "Error desconocido");
      callback(false); // Indica que hubo un error
      return;
    }

    personas.value = [...personas.value, personaCreada];
    store.increment();
    callback(true); // Indica que hubo un error
  } catch (error) {
    console.error(error);
    callback(false); // Indica que hubo un error
  }
};

const eliminarPersona = async (persona_id) => {
  if (!persona_id) {
    console.error("Error: persona_id es undefined");
    return;
  }

  // Metodo para eliminar una persona
  try {
    await fetch(API_URL + persona_id + "/", {
      method: "DELETE",
    });
    personas.value = personas.value.filter((u) => u.id !== persona_id);
  } catch (error) {
    console.error(error);
  }
};

const actualizarPersona = async (id, personaActualizada) => {
  // Metodo para actualizar una persona
  if (!id) {
    console.error("Error: id es undefined");
    return;
  }

  try {
    const response = await fetch(API_URL + personaActualizada.id + "/", {
      method: "PUT",
      body: JSON.stringify(personaActualizada),
      headers: { "Content-type": "application/json; charset=UTF-8" },
    });
    const personaActualizadaJS = await response.json();
    personas.value = personas.value.map((u) =>
      u.id === personaActualizada.id ? personaActualizadaJS : u
    );
  } catch (error) {
    console.error(error);
  }
};

// Fetch data when the component is mounted
onMounted(() => {
  listadoPersonas();
});
</script>

<style>
/* Estilos globales para todos los elementos button en la aplicacion */
button {
  background: #009435;
  border: 1px solid #009435;
}
</style>
