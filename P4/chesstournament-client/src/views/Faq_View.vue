<template>
  <div class="faq-container">
    <h1 class="faq-title">
      Frequently Asked Questions
    </h1>
    <div class="faq-list">
      <div
        v-for="(faq, index) in faqs"
        :key="index"
        class="faq-item"
      >
        <div
          class="faq-question"
          @click="toggle(index)"
        >
          <span>{{ faq.question }}</span>
          <span
            class="arrow"
            :class="{ open: openIndex === index }"
          >&#9662;</span>
        </div>
        <div
          v-if="openIndex === index"
          class="faq-answer"
        >
          <p>{{ faq.answer }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const faqs = [
  {
    question: '¿Qué es esta base de datos de torneos de ajedrez?',
    answer: 'Es una plataforma donde jugadores pueden buscar, ver y actualizar resultados de partidas en torneos de ajedrez.'
  },
  {
    question: '¿Necesito una cuenta para usar la plataforma?',
    answer: 'Cualquiera puede buscar torneos y ver resultados, pero solo los usuarios autenticados pueden actualizar resultados. Solo los administradores pueden crear torneos.'
  },
  {
    question: '¿Cómo puedo crear un torneo?',
    answer: 'Debes estar autenticado como administrador. Una vez dentro, verás el botón "Crear Torneo".'
  },
  {
    question: '¿Puedo editar un torneo existente?',
    answer: 'Solo los administradores pueden editar la información de un torneo. Los jugadores solo pueden ingresar resultados de sus partidas.'
  },
  {
    question: '¿Dónde puedo reportar errores o sugerencias?',
    answer: 'Puedes contactar al administrador del sitio a través del correo de soporte chesstable@chess.com'
  },
  {
    question: '¿Cómo pueden los administradores añadir jugadores a un torneo?',
    answer: 'Los jugadores se añaden mediante archivos en formato CSV. El archivo debe contener los nombres de las columnas en la primera fila, que deben coincidir con los campos del jugador (nombre, email, lichess_username, fide_rating_blitz, etc.). Para torneos en lichess, se requiere lichess_username. Para torneos presenciales (OTB), se requieren nombre y email. El sistema verificará automáticamente los nombres de usuario en lichess o usará los ratings FIDE para torneos presenciales.'
  }
]

const openIndex = ref(null)

function toggle(index) {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<style scoped>
.faq-container {
  max-width: 800px;
  margin: 3rem auto;
  padding: 2rem;
  background-color: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.faq-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #1f2937;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.faq-question {
  padding: 1rem 1.5rem;
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  color: #111827;
}

.faq-question:hover {
  background-color: #f3f4f6;
}

.arrow {
  transition: transform 0.3s ease;
}

.arrow.open {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  color: #374151;
  background-color: #fefefe;
}
</style>