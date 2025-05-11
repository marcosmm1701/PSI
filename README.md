# Chess Tournament Manager

**Chess Tournament Manager** es una plataforma web para la gestión integral de torneos de ajedrez, tanto presenciales (OTB) como en línea (Lichess). Permite a los administradores crear torneos, gestionar jugadores, registrar resultados y consultar rankings en tiempo real.

---

## 🧰 Tecnologías utilizadas

- **Backend:** Django + Django REST Framework
- **Frontend:** Vue 3 + Vite
- **Base de datos:** SQLite (modo desarrollo)
- **Autenticación:** Token Auth (DRF)
- **Tests automáticos:** Cypress
- **Linting:** ESLint + Prettier

---

## ⚙️ Funcionalidades principales

### 🏆 Gestión de Torneos
- Crear torneos con tipo:
  - **SR:** Round Robin
  - **SW:** Swiss
- Torneos presenciales (**OTB**) o en línea con Lichess (**LIC**).
- Configuración de puntos por victoria, empate y derrota.
- Configuración de sistemas de desempate múltiples (rankingList).

### 👤 Gestión de Jugadores
- Importación de jugadores por CSV:
  - OTB: `name,email`
  - LIC: `lichess_username`
- Validación automática del formato y datos.

### ♟️ Emparejamientos y Resultados
- Generación automática de rondas y partidas.
- Soporte para resultados:
  - Introducidos por jugadores (verificados por email).
  - Introducidos por el administrador.
  - Extraídos automáticamente desde Lichess con el ID de la partida.

### 📈 Clasificación
- Ranking actualizado en tiempo real.
- Cálculo usando múltiples sistemas de desempate:
  - Buchholz, Sonneborn-Berger, Plain Score, No. Wins, Black Times, etc.

### 🔐 Autenticación
- Solo usuarios autenticados pueden crear torneos.
- Solo el administrador puede modificar partidas ya finalizadas.

---
# Cómo ejecutar el proyecto

## En local

### Backend (Django)

cd P3

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver 8001

### Frontend (Vue 3)

cd P4

npm install

npm run dev

Accede a la URL: http://localhost:5173 y disfruta 😉

## En la nube (producción)

### Backend (Django)

Accede a la URL: https://psi-practica3-backend.onrender.com/api/v1/  (Espere unos segundos a que se reinicie la API)

Para iniciar sesión:  https://psi-practica3-backend.onrender.com/api/v1/token/login

Para acceder a tu usuario:  https://psi-practica3-backend.onrender.com/api/v1/users/me/

### Frontend (Vue 3)

Accede a la URL:  https://psi-practica4-frontend.onrender.com
