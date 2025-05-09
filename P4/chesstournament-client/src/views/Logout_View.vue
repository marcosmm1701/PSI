<template>
  <div class="logout-container" data-cy="logoutPage">
    <h1>Log Out</h1>
    <h2>You have been logged out</h2>
    <p>Thank you for visiting. Come back soon!</p>
    <router-link to="/login">
      <button class="logout-button">Login Again</button>
    </router-link>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

onMounted(() => {
  authStore.logout();
  // Redirigimos a home en 5 segundos
  setTimeout(() => {
    router.push("/");
  }, 5000);
});
</script>

<style scoped>
.logout-container {
  padding: 2rem;
  text-align: center;
  background-color: #f3f4f6;
  border-radius: 12px;
  margin: 2rem auto;
  max-width: 500px;
  box-shadow: 0 0 12px #e15050ac;
}

.logout-container h1 {
  font-size: 2rem;
  color: #d62828;
  margin-bottom: 0.5rem;
}

.logout-container h2 {
  font-size: 1.2rem;
  color: #6b7280;
  margin-bottom: 1rem;
}


.logout-button {
  background-color: hwb(220 35% 0%);
  color: white;
  border: none;
  padding: 10px 22px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, background-color 0.3s ease;
}

.logout-button:hover {
  background-color: #e63946;
  transform: scale(1.05);
}


.logout-button:hover {
  background-color: #2779bd;
}



.logout-container {
  animation: fadeInUp 0.8s ease;
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}



</style>
