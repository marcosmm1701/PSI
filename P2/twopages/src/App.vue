<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>
<template>
  <div>
    <h1>Ejemplo de uso de Router</h1>
    <nav>
      <router-link to="/page-one">Click for Page 1</router-link>&nbsp;
      <router-link to="/page-two">Click for Page 2</router-link>
    </nav>
    <router-view></router-view>
  </div>
</template>
<script>
export default {}
</script>
