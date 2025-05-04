<template>
    <div class="tournament-detail">
        <h2>Tournament: <em>{{ tournamentName }}</em></h2>
        <button @click="refreshPage" class="refresh-btn">Refresh Page</button>
        <p>Click the accordions below to expand/collapse the content.</p>

        <!-- Acordeones -->
        <details>

            <!-- Contenido claseificación-->
            <summary>Standing</summary>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Username</th>
                        <th>Points</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(player, index) in standingsData" :key="index">
                        <td>{{ player.rank }}</td>
                        <td>{{ player.name }}</td>
                        <td>{{ player.score }}</td>
                    </tr>
                </tbody>
            </table>
        </details>

        <details>
            <summary>Pairings/Results</summary>
            <div class="explanation">
                <p>
                    The abbreviations used in the "result" column are explained at the end of the page.
                    Press 📤 to update the game result. See the <router-link to="/faq">FAQ</router-link> for more
                    information.
                </p>
            </div>
            <div v-for="(round, index) in rounds" :key="index">
                <h3>{{ round.round_name }}</h3>
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
                        <tr v-for="(game, i) in round.games" :key="i">
                            <td>{{ i }}</td>
                            <td>{{ game.white_name }}</td>
                            <td class="result-cell">
                                <input v-model="game.result" placeholder="type gameID" />
                                <button @click="submitResult(game)">📤</button>
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
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const tournamentName = ref('');
const tournament = ref({}); // Objeto para almacenar el torneo
const rounds = ref([]); // Array para almacenar las rondas del torneo
const standingsData = ref([]); // Array para almacenar los datos del ranking

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

        tournament.value = TournamentsData.results.find(t => t.id == tournamentId);
        console.log("TOURNAMENT:", tournament.value);

        tournamentName.value = tournament.value.name; // Guardamos el nombre del torneo


        /*
        // Obtenemos el torneo especificado en la URL desde la API
        const response = await fetch(API_URL + "searchTournaments/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_string: tournamentName.value
            }),
        });

        if (!response.ok) {
            console.error('Error fetching tournaments:', data);
            return;
        }

        const data = await response.json();

        tournament.value = data[0] || [];
        */



        // Obtenemos las rondas del torneo con get_round_results, que nos devuelve las ronsas y las partidas del torneo
        //const tournamentId = tournament.value.id; // Obtenemos el ID del torneo

        const roundsresponse = await fetch(API_URL + "get_round_results/" + tournamentId);
        rounds.value = await roundsresponse.json();
        //console.log("ROUNDSDATA:", roundsresponse.value);
        console.log("ROUNDS:", rounds);



        // Obtenemos el ranking del torneo
        const standingsresponse = await fetch(API_URL + "get_ranking/" + tournamentId);
        const standingsRaw = await standingsresponse.json();

        // Convertimos el objeto en array
        const standingsArray = Object.values(standingsRaw);

        // Ordenamos el array por `rank`
        standingsData.value = standingsArray.sort((a, b) => a.rank - b.rank);

        console.log("STANDINGS SORTED:", standingsData.value);

    } catch (error) {
        console.error('Error fetching tournament:', error);
    }

});


function refreshPage() {
    window.location.reload();
}

function submitResult(game) {
    console.log('GAME:', game);
    console.log('RESULT:', game.result);
}
</script>

<style scoped>
.tournament-detail {
    padding: 2rem;
}

.refresh-btn {
    margin-bottom: 1rem;
    background-color: #e6f0ff;
    border: 1px solid #66a3ff;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 2rem;
}

th,
td {
    border: 1px solid #ccc;
    padding: 0.5rem;
    text-align: left;
}

.result-cell {
    display: flex;
    gap: 0.5rem;
}

input {
    padding: 0.3rem;
}

button {
    background-color: transparent;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
}

details summary {
    font-weight: bold;
    margin-top: 1rem;
    cursor: pointer;
}

.explanation {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #333;
}
</style>