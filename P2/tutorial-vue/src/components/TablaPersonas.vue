<!-- src/components/TablaPersonas.vue -->

<template>
    <!-- Contenedor principal del componente -->
    <div id="tabla-personas">
        <!-- Tabla para mostrar informacion de personas -->
        <table class="table">
            <!-- Encabezado de la tabla -->
            <thead>
                <!-- nombres de columnas -->
                <tr>
                    <th>Nombre</th>
                    <th>Apellido</th>
                    <th>Email</th>
                </tr>
            </thead>
            <!-- Cuerpo de la tabla con datos dinamicos -->
            <tbody>
                <!-- Iteracion sobre el array de personas utilizando v-for -->
                <tr v-for="persona in personas" :key="persona.id">
                    <!-- Celda de datos para el nombre de la persona -->
                    <td>{{ persona.nombre }}</td>
                    <!-- Celda de datos para el apellido de la persona -->
                    <td>{{ persona.apellido }}</td>
                    <!-- Celda de datos para el correo electronico de la persona -->
                    <td>{{ persona.email }}</td>
                </tr>
            </tbody>

        </table>
    </div>
</template>


<script setup>

// definicion del componente
defineOptions({
    // nombre del componente
    name: 'tabla-personas',
});

// declaramos y damos valor por defecto para la propiedad personas
const props = defineProps({
    personas: {type: Array, default: []},
});

</script>


<style scoped>
/* Estilos especificos del componente con el modificador "scoped" */
</style>
