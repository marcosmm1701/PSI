<template>
    <div class="create-tournament">
        <h1>Creating Tournament...</h1>

        <div v-if="!authStore.isAuthenticated" class="unauth-msg">
            <p>You must be logged in to access this page.</p>
            <router-link to="/login"><button>Go to Login</button></router-link>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="form-box">
            <label>
                Name:
                <input v-model="form.name" required placeholder="Introduzca el nombre del torneo" />
            </label>

            <label>
                Tournament Type:
                <select v-model="form.tournament_type" required>
                    <option value="SWISS">Swiss</option>
                    <option value="ROUND_ROBIN">Round Robin</option>
                </select>
            </label>

            <label>
                Board Type:
                <select v-model="form.board_type" required>
                    <option value="OTB">OTB</option>
                    <option value="LICHESS">Lichess</option>
                </select>
            </label>

            <label>
                Tournament Speed:
                <select v-model="form.tournament_speed" required>
                    <option value="BULLET">Bullet</option>
                    <option value="BLITZ">Blitz</option>
                    <option value="RAPID">Rapid</option>
                    <option value="CLASSICAL">Classical</option>
                </select>
            </label>

            <label>
                Ranking Systems (select in order):
                <details class="ranking-dropdown">
                    <summary>Click to select ranking systems</summary>
                    <div class="ranking-checkboxes">
                        <label v-for="system in allRankingSystems" :key="system.value">
                            <input type="checkbox" :value="system.value"
                                :checked="form.rankingList.includes(system.value)"
                                @change="handleRankingChange(system.value, $event)" />
                            {{ system.label }}
                            <span v-if="form.rankingList.includes(system.value)">
                                ({{ form.rankingList.indexOf(system.value) + 1 }})
                            </span>
                        </label>
                    </div>
                </details>
            </label>


            <div class="checkbox-row">
                <label for="only_administrative">Only Administrative:</label>
                <input id="only_administrative" type="checkbox" v-model="form.only_administrative" />
            </div>


            <div class="points-section">
                <label>Win Points: <input type="number" step="0.1" v-model.number="form.win_points" /></label>
                <label>Draw Points: <input type="number" step="0.1" v-model.number="form.draw_points" /></label>
                <label>Lose Points: <input type="number" step="0.1" v-model.number="form.lose_points" /></label>
            </div>

            <label>
                Players CSV:
                <textarea v-model="form.players" placeholder="Add CSV content here..."></textarea>
            </label>

            <button type="submit" :disabled="loading">Create Tournament</button>

            <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
            <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
        </form>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_DJANGOURL
const authStore = useAuthStore()
const router = useRouter()

const form = ref({
    name: '',
    tournament_type: 'SWISS',
    board_type: 'OTB',
    tournament_speed: 'RAPID',
    only_administrative: false,
    win_points: 1.0,
    draw_points: 0.5,
    lose_points: 0.0,
    players: '',
    rankingList: [] // ordered list
})

const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

// Ranking systems manually defined
const allRankingSystems = [
    { value: 'BU', label: 'Buchholz' },
    { value: 'BC', label: 'Buchholz Cut 1' },
    { value: 'BA', label: 'Buchholz Average' },
    { value: 'SB', label: 'Sonneborn-Berger' },
    { value: 'PS', label: 'Plain Score' },
    { value: 'WI', label: 'No. Wins' },
    { value: 'BT', label: 'Black Times' }
]

// Keep selection in order
function handleRankingChange(value, event) {
    if (event.target.checked) {
        // Añadir al final
        if (!form.value.rankingList.includes(value)) {
            form.value.rankingList.push(value)
        }
    } else {
        // Eliminar
        form.value.rankingList = form.value.rankingList.filter(v => v !== value)
    }
}



async function handleSubmit() {
    errorMsg.value = ''
    successMsg.value = ''
    loading.value = true

    try {
        const res = await fetch(API_URL + 'createtournament/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authStore.token}`
            },
            body: JSON.stringify({ ...form.value })
        })

        const data = await res.json()

        if (!res.ok) {
            throw new Error(data.message || 'Tournament creation failed.')
        }

        successMsg.value = 'Tournament created successfully!'
        setTimeout(() => {
            router.push('/')
        }, 2000)
    } catch (err) {
        errorMsg.value = err.message
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.create-tournament {
    max-width: 900px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
}

h1 {
    text-align: center;
    margin-bottom: 1.5rem;
}

.form-box {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

label {
    display: flex;
    flex-direction: column;
    font-weight: 600;
    color: #374151;
}

input,
select,
textarea {
    padding: 0.5rem;
    margin-top: 0.3rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 1rem;
}

textarea {
    min-height: 100px;
}

.points-section {
    display: flex;
    gap: 1rem;
}

button {
    padding: 0.6rem;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background-color: #1e40af;
}

.error-msg {
    color: #dc2626;
    font-weight: 600;
}

.success-msg {
    color: #16a34a;
    font-weight: 600;
}

.unauth-msg {
    text-align: center;
    color: #b91c1c;
    font-weight: bold;
}

.ranking-dropdown {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid #ccc;
    padding: 0.5rem;
    border-radius: 8px;
    background: #f9f9f9;
}

.ranking-dropdown summary {
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 0.5rem;
}

.ranking-checkboxes {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    margin-top: 0.5rem;
}

.ranking-checkboxes label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

</style>