<template>
  <div class="tournament-detail">
    <h2 data-cy="tournament-title">
      Tournament: <em>{{ tournamentName }}</em>
    </h2>
    <button class="refresh-btn" @click="refreshPage">Refresh Page</button>
    <p>Click the accordions below to expand/collapse the content.</p>

    <!-- Acordeones -->
    <details>
      <!-- Contenido claseificación-->
      <summary data-cy="standing-accordion-button">Standing</summary>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Username</th>
            <th>Points</th>
            <th>Nº Wins</th>
            <th>Nº Black times</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in standingsData"
            :key="index"
            :data-cy="'ranking-' + (Number(index) + 1)"
          >
            <td>{{ player.rank }}</td>
            <td>{{ player.name }}</td>
            <td>{{ player.score }}</td>
            <td>{{ Number(player.WI).toFixed(2) }}</td>
            <td>{{ Number(player.BT).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </details>

    <details>
      <summary>Pairings/Results</summary>
      <div v-if="tournament?.board_type === 'OTB'" class="otb-banner">
        <strong>OTB</strong>
      </div>
      <div v-if="tournament?.board_type === 'LIC'" class="lic-banner">
        <strong>LICHESS</strong>
      </div>

      <div class="explanation">
        <p>
          The abbreviations used in the "result" column are explained at the end
          of the page. Press 📤 to update the game result. See the
          <router-link to="/faq"> FAQ </router-link> for more information.
        </p>
      </div>
      <div v-for="(round, roundIndex) in rounds" :key="roundIndex">
        <h3 :data-cy="'round_' + (Number(roundIndex) + 1)">
          {{ round.round_name }}
        </h3>
        <table>
          <thead>
            <tr>
              <th>Table</th>
              <th>White</th>
              <th>Result</th>
              <th>Black</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(game, i) in round.games"
              :key="i"
              :data-cy="'game_' + (Number(roundIndex) + 1) + '_' + Number(i)"
            >
              <td>
                {{ i }}
              </td>

              <td>{{ game.white_name }}</td>
              <td class="result-cell">
                <span
                  v-if="game.result != '*'"
                  :data-cy="'input-' + (Number(roundIndex) + 1) + '-' + i"
                >
                  {{ getReadableResult(game.result) }}
                </span>

                <div v-if="game.result === '*'">
                  <template v-if="tournament.board_type === 'LIC'">
                    <input
                      v-model="game.lichessGameId"
                      placeholder="Lichess game ID"
                      :data-cy="'input-' + (Number(roundIndex) + 1) + '-' + i"
                    />
                    <button
                      :data-cy="'button-' + (Number(roundIndex) + 1) + '-' + i"
                      @click="submitLichessResult(game)"
                    >
                      📤
                    </button>
                  </template>
                  <template v-if="tournament.board_type === 'OTB'">
                    <label><strong>Result:</strong></label>
                    <select
                      v-model="game.newResult"
                      :data-cy="'select-' + (Number(roundIndex) + 1) + '-' + i"
                    >
                      <option disabled value="">Select result</option>
                      <option value="White wins (1-0)">White wins (1-0)</option>
                      <option value="Black wins (0-1)">Black wins (0-1)</option>
                      <option value="Draw (1/2-1/2)">Draw (1/2-1/2)</option>
                    </select>
                    <button
                      :data-cy="'button-' + (Number(roundIndex) + 1) + '-' + i"
                      @click="submitOTBResult(game)"
                    >
                      📤
                    </button>
                  </template>
                </div>

                <div v-if="authStore.isAuthenticated">
                  <!-- Resultado ya asignado, pero eres admin -->
                  <label><strong>Result (Admin): </strong></label>
                  <select
                    v-model="game.newResult"
                    :data-cy="
                      'select-admin-' + (Number(roundIndex) + 1) + '-' + i
                    "
                  >
                    <option disabled value="">Select result</option>
                    <option value="White wins (1-0)">White wins (1-0)</option>
                    <option value="Black wins (0-1)">Black wins (0-1)</option>
                    <option value="Draw (1/2-1/2)">Draw (1/2-1/2)</option>
                  </select>
                  <button
                    :data-cy="
                      'button-admin-' + (Number(roundIndex) + 1) + '-' + i
                    "
                    @click="submitResultAdmin(game)"
                  >
                    📤
                  </button>
                </div>
              </td>

              <td>{{ game.black_name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const tournamentName = ref("");
const tournament = ref({}); // Objeto para almacenar el torneo
const rounds = ref([]); // Array para almacenar las rondas del torneo
const standingsData = ref([]); // Array para almacenar los datos del ranking
const authStore = useAuthStore();

const API_URL = import.meta.env.VITE_DJANGOURL;

onMounted(async () => {
  try {
    // Obtenemos todos los torneos desde la API
    const responseTournaments = await fetch(API_URL + "tournaments");
    const TournamentsData = await responseTournaments.json();
    console.log("TOURNAMENTS TODOOS:", TournamentsData.results);

    //filtramos para encontrar el que tiene el nombre que buscamos
    const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL
    console.log("TOURNAMENT ID:", tournamentId);

    tournament.value = TournamentsData.results.find(
      (t) => t.id == tournamentId
    );
    console.log("TOURNAMENT:", tournament.value);

    tournamentName.value = tournament.value.name; // Guardamos el nombre del torneo
    console.log("TOURNAMENT NAME:", tournamentName.value);

    // Obtenemos las rondas del torneo con get_round_results, que nos devuelve las ronsas y las partidas del torneo
    //const tournamentId = tournament.value.id; // Obtenemos el ID del torneo

    const roundsresponse = await fetch(
      API_URL + "get_round_results/" + tournamentId
    );
    rounds.value = await roundsresponse.json();
    //console.log("ROUNDSDATA:", roundsresponse.value);
    console.log("ROUNDS:", rounds.value);

    // Obtenemos el ranking del torneo
    const standingsresponse = await fetch(
      API_URL + "get_ranking/" + tournamentId
    );
    const standingsRaw = await standingsresponse.json();

    // Convertimos el objeto en array
    const standingsArray = Object.values(standingsRaw);
    console.log("STANDINGS:", standingsArray);
    // Ordenamos el array por `rank`
    standingsData.value = standingsArray.sort((a, b) => a.rank - b.rank);

    console.log("STANDINGS SORTED:", standingsData.value);

    if (tournament.value.board_type === "OTB") {
      console.log("This is an OTB tournament.");
    } else if (tournament.value.board_type === "LIC") {
      console.log("This is an LICHESS tournament.");
    } else {
      console.log("Unknown tournament type.");
    }
  } catch (error) {
    console.error("Error fetching tournament:", error);
  }
});

function getReadableResult(result) {
  switch (result) {
    case "w":
      return "White wins (1-0)";
    case "b":
      return "Black wins (0-1)";
    case "d":
      return "Draw (½-½)";
    case "=":
      return "Draw (½-½)";
    default:
      return result;
  }
}

async function submitLichessResult(game) {
  const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL

  // Comprobamos que se ha itroducido el ID de la partida de Lichess
  if (!game.lichessGameId) {
    alert("Please enter a Lichess game ID.");
    return;
  }

  console.log("Game:", game);
  console.log("Lichess Game ID:", game.lichessGameId);

  try {
    const response = await fetch(API_URL + "update_lichess_game/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        game_id: game.id,
        lichess_game_id: game.lichessGameId,
      }),
    });

    const data = await response.json();

    if (response.ok && data.result === true) {
      alert("Lichess result fetched and game updated.");
      //game.result = resultValue.value;
      game.lichessGameId = ""; // limpiamos input
    } else {
      alert(data.message || "Failed to fetch Lichess result.");
    }
  } catch (err) {
    console.error(err);
    alert("An error occurred while submitting the Lichess game ID.");
  }

  fetchParings();
  fetchStandings();
  //onMounted(); // Refetch the tournament data
  router.push("/tournamentdetail/" + tournamentId); // Redirigimos para actualizar la vista
}

async function submitOTBResult(game) {
  const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL

  //Obtenemos los jugadores del torneo para la comprobacion de OTB
  const playersResponse = await fetch(API_URL + "get_players/" + tournamentId);
  const players = await playersResponse.json();
  console.log("PLAYERS:", players);

  const email = prompt("Please enter the email used to join this tournament:");
  if (!email) {
    alert("You must enter an email.");
    return;
  }

  const resultValue = ref("");

  if (game.newResult === "White wins (1-0)") {
    resultValue.value = "w";
  } else if (game.newResult === "Black wins (0-1)") {
    resultValue.value = "b";
  } else if (game.newResult === "Draw (1/2-1/2)") {
    resultValue.value = "d";
  }

  // Validamos el email
  const emailBuscado = email.toLowerCase();
  const existe = players.some((p) => p.email === emailBuscado);
  if (!existe) {
    alert("Email does not match with any player in the game");
    return;
  }
  console.log("Game ID:", game.id);
  console.log("New Result:", game.newResult);
  console.log("Result VALEU:", resultValue.value);
  console.log("Email:", email);
  console.log("Game:", game);

  try {
    const response = await fetch(API_URL + "update_otb_game/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        game_id: game.id,
        otb_result: resultValue.value,
        email: email,
      }),
    });
    console.log("Response:", response);

    const data = await response.json();

    if (response.ok) {
      alert("Game updated successfully!");
      game.result = resultValue.value;
      game.newResult = ""; // Reset select
    } else {
      alert(data.error || "Failed to update result. Something went wrong.");
    }
  } catch (err) {
    console.error(err);
    alert("An error occurred while submitting the result.");
  }

  fetchStandings();
  router.push("/tournamentdetail/" + tournamentId); // Redirigimos para actualizar la vista
}

async function submitResultAdmin(game) {
  const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL

  const resultValue = ref("");

  if (game.newResult === "White wins (1-0)") {
    resultValue.value = "w";
  } else if (game.newResult === "Black wins (0-1)") {
    resultValue.value = "b";
  } else if (game.newResult === "Draw (1/2-1/2)") {
    resultValue.value = "d";
  }

  console.log("Game ID:", game.id);
  console.log("New Result:", resultValue.value);
  console.log("Game:", game);
  console.log("Auth token:", authStore.token);

  try {
    const response = await fetch(API_URL + "admin_update_game/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${authStore.token}`,
      },
      body: JSON.stringify({
        game_id: game.id,
        otb_result: resultValue.value,
      }),
    });
    console.log("Response:", response);

    const data = await response.json();

    if (response.ok) {
      alert("Game updated successfully!");
      game.result = resultValue.value;
      game.newResult = ""; // Reset select
    } else {
      alert(data.error || "Failed to update result. Something went wrong.");
    }
  } catch (err) {
    console.error(err);
    alert("An error occurred while submitting the result.");
  }

  //fetchParings()
  fetchStandings();
  router.push("/tournamentdetail/" + tournamentId); // Redirigimos para actualizar la vista
}

async function fetchStandings() {
  const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL
  // Obtenemos el ranking del torneo
  const standingsresponse = await fetch(
    API_URL + "get_ranking/" + tournamentId
  );
  const standingsRaw = await standingsresponse.json();

  // Convertimos el objeto en array
  const standingsArray = Object.values(standingsRaw);

  // Ordenamos el array por `rank`
  standingsData.value = standingsArray.sort((a, b) => a.rank - b.rank);
}

async function fetchParings() {
  const tournamentId = route.params.id; // Obtenemos el ID del torneo desde la URL
  try {
    const roundsresponse = await fetch(
      API_URL + "get_round_results/" + tournamentId
    );
    rounds.value = await roundsresponse.json();
    //console.log("ROUNDSDATA:", roundsresponse.value);
    console.log("ROUNDS FECHING:", rounds.value);
  } catch (error) {
    console.error("Error fetching tournament:", error);
  }
}

function refreshPage() {
  window.location.reload();
}
</script>

<style scoped>
.tournament-detail {
  padding: 2rem;
  background-color: rgba(0, 0, 0, 0.6); /* semi-transparente para contraste sobre imagen */
  color: #ffffff; /* texto blanco para buen contraste */
  border-radius: 10px;
  backdrop-filter: blur(5px); /* efecto moderno con desenfoque */
}

h2,
h3,
details summary {
  color: #ffffff;
}

.refresh-btn {
  margin-bottom: 1rem;
  background-color: #e6f0ff;
  border: 1px solid #66a3ff;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  color: #004080;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.8); /* fondo semitransparente para mejor contraste */
}


th {
  background-color: #004080;
  color: rgb(12, 12, 12);
  padding: 0.75rem;
  font-weight: bold;
  text-align: left;
}

td, tr {
  background-color: rgba(10, 10, 10, 0.95);
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
}

tr:last-child td {
  border-bottom: none;
}

input, select {
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #0d0c0c;
  background-color: #f9f9f9;
}

.result-cell {
  display: flex;
  gap: 0.5rem;
}

button {
  background-color: #66a3ff;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: white;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
}

.otb-banner,
.lic-banner {
  background-color: #ffeeba;
  color: #856404;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #ffd966;
  text-align: center;
  font-weight: bold;
}

details summary {
  font-weight: bold;
  margin-top: 1rem;
  cursor: pointer;
}


.explanation {
  padding: 0.5rem;
  text-align: left;
}
</style>
