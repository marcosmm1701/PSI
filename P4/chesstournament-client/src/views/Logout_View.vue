<template>
  <div
    class="logout-container"
    data-cy="logoutPage"
  >
    <h1>Log Out</h1>
    <h2>You have been logged out</h2>
    <p>Thank you for visiting. Come back soon!</p>
    <router-link to="/login">
      <button class="logout-button">
        Login Again
      </button>
    </router-link>
  </div>
</template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  import { onMounted } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  onMounted(() => {
    authStore.logout()
    // Redirigimos a home en 5 segundos
    setTimeout(() => {
      router.push('/')
    }, 5000)
    
  })
  </script>
  
  <style scoped>
  .logout-container {
    padding: 2rem;
    text-align: center;
    background-color: #f3f4f6;
    border-radius: 12px;
    margin: 2rem auto;
    max-width: 400px;
    box-shadow: 0 0 12px #e15050ac;
  }
  
  .logout-button {
    background-color: #3490dc;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    margin-top: 1rem;
    transition: background-color 0.3s ease;
  }
  
  .logout-button:hover {
    background-color: #2779bd;
  }
  </style>
  