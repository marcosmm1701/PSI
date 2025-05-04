<template>
  <div class="Welcome-message-User" v-if="!authStore.isAuthenticated">
    <p>
      Welcome to the Chess Tournament Database.
      This database features the unique ability for players to update the results of their games.
      To create tournaments, an administrative account is required. However, any player can enter the result of a game.
    </p>
    <p>
      You can use the search button to fund tournaments by name. For further information, please refer to the
      <router-link :to="`/FAQ/`">FAQ</router-link> section.
    </p>
  </div>

  <div class="Welcome-message-Admin" v-if="authStore.isAuthenticated">
    <p>
      Hello, you are logged in as an administrator. Remember, with great prowe comes great responsibility.
    </p>
    <p>
      As an administratos you can create tournaments and edit or update the results of games, rounds, and tournaments.
    </p>
    <p>
      To create a new tournament, press the <strong>Create Tournament</strong> button. To edit or update games, rounds, or
      tournaments, select the desired tournament.
    </p>
    <router-link to="/createTournament">
      <button class="create-tournament-button">Create Tournament</button>
    </router-link>
  </div>

  <!--Seccion de Torneos-->
  <div class="tournament-section">

    <!-- Lista principal paginada -->
    <div class="listado-torneos">
      <h3>Tournaments</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tournaments" :key="t.id">
            <td>
              <router-link :to="`/tournamentdetail/${t.id}`">{{ t.name }}</router-link>
            </td>
            <td>{{ formatDate(t.start_date) }}</td>
            <!-- Hemos hecho la funcion formatDate para que no de muestre la hora -->
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">Previous</button>
        <!--<span>Page {{ currentPage }} of {{ totalPages }}</span>-->
        <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
      </div>
    </div>

    <!-- Búsqueda -->
    <div class="search-box">
      <input v-model="searchQuery" placeholder="Search..." />
      <button @click="search">Search</button>
      <table v-if="filteredTournaments.length">
        <thead>
          <tr>
            <th>Name</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTournaments" :key="t.id">
            <td><router-link :to="`/tournamentdetail/${t.id}`">{{ t.name }}</router-link></td>
            <td>{{ formatDate(t.start_date) }}</td>
            <!-- Hemos hecho la funcion formatDate para que no de muestre la hora -->
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>





<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore(); // Instancia del store de autenticación

const tournaments = ref([]);
const currentPage = ref(1);
const pageSize = 5;

const searchQuery = ref('');
const filteredTournaments = ref([]);

// Paginación computada
const totalPages = computed(() => {
  return Math.ceil(tournaments.value.length / pageSize);
});

const paginatedTournaments = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return tournaments.value.slice(start, start + pageSize);
});

// Función para formatear la fecha
const formatDate = (datetimeString) => {
  return datetimeString.split('T')[0];
}

const API_URL = import.meta.env.VITE_DJANGOURL;

// Fetch inicial
onMounted(async () => {
  try {
    const torneos = await fetch(API_URL + 'tournaments/');  // Hacemos la petición a la API
    const data = await torneos.json();                      // Convertimos la respuesta a JSON
    tournaments.value = data.results || [];                 // Guardamos los torneos en la variable tournaments
    console.log("TOURNAMENTS:", tournaments.value);                       // Mostramos los torneos en la consola
  } catch (error) {
    console.error('Error fetching tournaments:', error);
  }
});

// Funciones de navegación
function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

// Búsqueda
async function search() {
  const query = searchQuery.value.toLowerCase();

  const response = await fetch(API_URL + "searchTournaments/", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      search_string: query
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    console.error('Error fetching tournaments:', data);
    return;
  }
  filteredTournaments.value = data || [];
}
</script>


<style scoped>
.home-container {
  padding: 1rem;
}

.Welcome-message-User,
.Welcome-message-Admin {
  width: 100%;
  height: 250px;
  background-color: #f5f5f5;
  padding: 40px 30px;
  margin-bottom: 2rem;
  border-radius: 8px;
}



.tournament-section {
  padding: 1rem;
  display: flex;
  gap: 2rem;
  /* Espacio entre elementos */
  justify-content: space-between;
  /* Distribuye el espacio */
  align-items: flex-start;
  /* Alinea los elementos en la parte superior */
}

.listado-torneos,
.search-box {
  width: 100%;
  height: 300px;
  flex: 1;
  min-width: 300px;
  /* Para evitar que se hagan demasiado pequeñas en pantallas pequeñas */
}

.listado-torneos {
  flex: 2;
  /* Ocupa 2/3 del espacio disponible */
  background-color: #141a22;
  color: white;
  padding: 20px;
  border-radius: 8px;
}

.search-box {
  flex: 1;
  /* Ocupa 1/3 del espacio disponible */
  background-color: #9cc4f9;
  color: white;
  padding: 20px;
  border-radius: 8px;
  position: sticky;
  top: 20px;
  /* Para que quede fijo al hacer scroll */
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th,
td {
  border: 1px solid #ccc;
  padding: 0.5rem;
}

.pagination {
  margin-top: 1rem;
  display: flex;
  justify-content: space-between;
}

input {
  padding: 0.4rem;
  margin-right: 0.5rem;
}

button {
  padding: 0.4rem 0.8rem;
  cursor: pointer;
}

.create-tournament-button {
  width: 100%;
  background-color: #4CAF50; /* Verde vibrante */
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 50px; /* Bordes completamente redondeados */
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>