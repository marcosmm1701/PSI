<template>
  <div class="Welcome-message-User" v-if="!authStore.isAuthenticated">
    <h2 class="welcome-title">Welcome to the Chess Tournament Database</h2>
    <p class="welcome-text">
      Welcome to the Chess Tournament Database.
      This database features the unique ability for players to update the results of their games.
      To create tournaments, an administrative account is required. However, any player can enter the result of a game.
    </p>
    <p class="welcome-text">
      You can use the search button to fund tournaments by name. For further information, please refer to the
      <router-link :to="`/FAQ/`">FAQ</router-link> section.
    </p>
  </div>

  <div class="Welcome-message-Admin" data-cy="admin-log" v-if="authStore.isAuthenticated">
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
      <button class="create-tournament-button" data-cy=create-Tournament-button>Create Tournament</button>
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
          <tr v-for="t in tournaments" :key="t.id" :data-cy="`${t.name}`">
            <td>
              <router-link :to="`/tournamentdetail/${t.id}`">{{ t.name }}</router-link>
            </td>
            <td>{{ formatDate(t.start_date) }}</td>
            <!-- Hemos hecho la funcion formatDate para que no de muestre la hora -->
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1" data-cy="previous-button">Previous</button>
        <!--<span>Page {{ currentPage }} of {{ totalPages }}</span>-->
        <button @click="nextPage" :disabled="currentPage === totalPages" data-cy="next-button">Next</button>
      </div>
    </div>

    <!-- Búsqueda -->
    <div class="search-box">
      <input v-model="searchQuery" data-cy="input-search" placeholder="Search..." />
      <button @click="search" data-cy=submit-search>Search</button>
      <table v-if="filteredTournaments.length">
        <thead>
          <tr>
            <th>Name</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTournaments" :key="t.id" :data-cy="`search-${t.name}`">
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
const totalPages = ref(1);

const searchQuery = ref('');
const filteredTournaments = ref([]);

// Función para formatear la fecha
const formatDate = (datetimeString) => {
  return datetimeString.split('T')[0];
}

const API_URL = import.meta.env.VITE_DJANGOURL;


async function fetchTournaments(page = 1) {
  try {
    const response = await fetch(`${API_URL}tournaments/?page=${page}`);
    const data = await response.json();
    tournaments.value = data.results;
    totalPages.value = Math.ceil(data.count / 10); // count viene del backend
    currentPage.value = page;
  } catch (error) {
    console.error('Error fetching tournaments:', error);
  }
}


onMounted(() => {
  fetchTournaments();
});

function nextPage() {
  if (currentPage.value < totalPages.value) {
    fetchTournaments(currentPage.value + 1);
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    fetchTournaments(currentPage.value - 1);
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
  background: linear-gradient(to right, #e0f7fa, #e1f5fe);
  padding: 2rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.welcome-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.welcome-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
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
  height: auto;
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
  overflow: auto;
  /* Para que quede fijo al hacer scroll */
}

.search-box input {
  width: 80%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

.search-box button {
  padding: 10px 16px;
  border-radius: 8px;
  background-color: #1976d2;
  color: white;
  border: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.search-box button:hover {
  background-color: #125ea5;
}


table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background-color: #d5f1fa;
  color: #333;
  border-radius: 8px;
  overflow: hidden;
}

thead {
  background-color: #1976d2;
  color: white;
  text-align: left;
}

th,
td {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody tr:hover {
  background-color: #e3f2fd;
  cursor: pointer;
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
  border-radius: 50px;
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