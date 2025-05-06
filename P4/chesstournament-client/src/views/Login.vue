<template>
    <!-- Contenedor principal que agrupa todos los elementos del componente -->
    <div class="login-container">
        <h2 class="login-tittle">Login</h2>

        <!-- Formulario para hacer login. -->
        <form @submit.prevent="handleLogin">   <!-- Cuando escucha el evento submit, se llama a la función handleLogin -->
            <div class="input-group">
                <input
                    id="username"
                    v-model="username"
                    type="text"
                    placeholder="Username"
                    data-cy="username"
                    class="login-input"
                /> 
            </div> 

            <div class="input-group">
                <input
                    id="password"
                    v-model="password"
                    type="password"
                    placeholder="Password"
                    data-cy="password"
                    class="login-input"
                />
            </div>
            
            <button type="submit" class="login-button" data-cy="login-button">Log in</button>
        </form>
        <!-- Cuando la variable errorMessage esté a true, se muestra el mensaje de {{ errorMesage }}-->
        <p v-if="errorMessage" class="error-message" data-cy="error-message">{{ errorMessage }}</p>
    </div>

</template>

<script setup>
// Importar las dependencias necesarias
import { ref } from 'vue';
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'


const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();         // Instancia del router para redirigir después de iniciar sesión
const authStore = useAuthStore()    // Instancia del store de autenticación


const API_URL = import.meta.env.VITE_DJANGOURL; // Obtenemos la URL del backend desde las variables de entorno
// console.log("API_URL:", API_URL); 

const handleLogin = async () => {
    try {
        // Realizamos la petición POST al backend para hacer login
        const response = await fetch(API_URL + "token/login", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username.value,
                password: password.value,
            }),
        });

        const data = await response.json();

        // Si la respuesta no es 200, lanzamos un error
        if (!response.ok) {
            errorMessage.value = data.detail || "Error: Invalid username or password";
            return;
        }

        // Si la respuesta es correcta, obtenemos el token y lo guardamos en el store
        authStore.setToken(data.auth_token);
        
        //console.log("Token:", data.auth_token);

        // Redirigimos al home
        router.push('/')
    } catch (err) {
        errorMessage.value = 'Error: Invalid username or password'
    }
}


</script>



<style scoped>

/* Importamos, una fuente redondeada de Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');


.login-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 450px;
  margin: auto;
  padding: 40px 40px;
  background: white;
  border-radius: 20px; /* Bordes muy redondeados y bonitos ;)*/
  box-shadow: 0 10px 30px #000000e4;
  text-align: center;
  font-family: 'Nunito', sans-serif; /* Para fuente redondeada */
}

.login-tittle {
  font-size: 3rem;
  margin-bottom: 2rem;
  color: #070808;
  font-weight: 700; /* Grosor de fuente más pronunciado */
  letter-spacing: -0.5px; /* Espaciado más compacto */
}

.input-group {
  margin-bottom: 1.8rem;
}

.login-input {
  width: 100%;
  padding: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px; /* Bordes redondeados */
  font-size: 1rem;
  font-family: 'Nunito', sans-serif;
  text-align: center;
  outline: none;
  transition: all 0.3s ease;
  background-color: #f5edaf;
}

.login-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.login-input::placeholder {
  color: #a0aec0;
  font-family: 'Nunito', sans-serif;
}

.login-button {
  width: 100%;
  padding: 15px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 12px; /* Igual de redondeado que los inputs */
  font-size: 1rem;
  font-weight: 700;
  font-family: 'Nunito', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.login-button:hover {
  background-color: #5a67d8;
  transform: translateY(-2px); /* Efecto de levitación */
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.error-message {
  color: #e53e3e;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  font-weight: 600;
}
</style>