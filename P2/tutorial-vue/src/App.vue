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
        <formulario-persona /> <!-- Inclusion del componente "FormularioPersona" -->
        <!-- Inclusion del componente "TablaPersonas" -->
        <tabla-personas :personas="personas" /> <!-- Para pasar los datos a TablaPersonas.vue -->
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref } from 'vue';

// Importacion del componente "FormularioPersona"
import FormularioPersona from '@/components/FormularioPersona.vue'
// Importacion del componente "TablaPersonas"
import TablaPersonas from '@/components/TablaPersonas.vue'


// Definicion del componente Vue
defineOptions({
  // Nombre del componente
  name: 'app',
});


// Declaracion de una variable reactiva "personas" usando "ref"
const personas = ref([
  {
    id: 1,
    nombre: 'Jon',
    apellido: 'Nieve',
    email: 'jon@email.com',
  },
  {
    id: 2,
    nombre: 'Tyrion',
    apellido: 'Lannister',
    email: 'tyrion@email.com',
  },
  {
    id: 3,
    nombre: 'Daenerys',
    apellido: 'Targaryen',
    email: 'daenerys@email.com',
  },
]);


</script>

<style>
/* Estilos globales para todos los elementos button en la aplicacion */
button {
  background: #009435;
  border: 1px solid #009435;
}
</style>