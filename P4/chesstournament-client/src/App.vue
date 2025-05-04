<!-- App.vue -->
<template>
  <div class="app-container">
    <!-- Barra de navegación (común a todas las páginas) -->
    <nav class="navbar">
      <div class="navbar-brand">Chess-T-DB</div>
      <div class="navbar-links">
        <router-link to="/">Home</router-link>
        <router-link to="/login">Admin Log-In</router-link>
        <router-link to="/logout">Log-Out</router-link>
        <router-link to="/faq">FAQ</router-link>
      </div>
    </nav>

    <!-- Contenedor principal donde se cargarán las vistas -->
    <main class="main-content">
      <router-view /> <!-- Aquí se inyectarán los componentes de cada ruta -->
    </main>

    <!-- Footer común a todas las páginas -->
    <footer class="footer">
      © 2024 Copyright: I. Serena y M. Muñoz
    </footer>
  </div>
</template>

<script setup>
// No necesitas lógica especial aquí a menos que necesites
// manejar algo a nivel de toda la aplicación

import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
  /* scoped: Estilos específicos para este componente */

  .app-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    /* asegura que el contenedor tenga al menos la altura de la pantalla */
    min-width: 120vh; /* ESTO ME ACABA DE SALVAAAR LA VIDAAAA*/

  }

  /* Barra de navegación horizontal */
  .navbar {
    width: 100%;
    /* Ocupa el 100% del ancho disponible */
    height: 80px;
    /* Altura de la barra de navegación */
    z-index: 1000; 
    /* Asegura que la barra de navegación esté por encima de otros elementos */
    background-color: #2c3e50;
    /* Color de fondo azul oscuro */
    padding: 16px 32px;
    /* Espaciado interno (tamaño objeto): 16px arriba/abajo, 32px izquierda/derecha */
    position: fixed;
    /* Posicionamiento fijo en la ventana */
    top: 0;
    /* Pegado al borde superior */
    left: 0;
    /* Pegado al borde izquierdo */
    display: flex;
    /* Usa el modelo Flexbox para disposición */
    align-items: center;
    /* Centra verticalmente los elementos hijos */
    color: white;
    /* Color de texto blanco */
  }


  .navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
    white-space: nowrap;
  }

  .navbar-links {
    display: flex;
    gap: 1.5rem;
    margin-right: auto;
    /* Empuja los enlaces a la izquierda */
  }

  .navbar-links a {
    color: white;
    text-decoration: none;
  }

  .navbar-links a:hover {
    text-decoration: underline;
  }

  .main-content {
    flex: 1;
    width: 100%;
    margin-top: 80px;
    /* espacio para la navbar fija */
    padding: 1rem;
    padding-bottom: 100px;
    /* espacio para que no se solape con el footer */
  }

  .footer {
    width: 100%;
    position: fixed;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 1rem;
    background-color: #f8f9fa;
    border-top: 1px solid #ddd;
    z-index: 1000;
  }
</style>