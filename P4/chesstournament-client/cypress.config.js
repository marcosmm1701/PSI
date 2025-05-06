const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    defaultCommandTimeout: 10000, // 10 seconds
    // append baseUrl to all URL used in the tests
    baseUrl: "http://localhost:5173",
    //specPattern: "cypress/e2e/**/*.{js,jsx,ts,tsx}",
  },
  // centralice some variables as username and password
  // use then in the test with "Cypress.env('username')"
  env: {
    username: "y",
    password: "y",
    python: "/home/marcos1701/Escritorio/Marcos.M/PSI/PSI/P4/chesstournament-client/venv/bin/python3",
    manage: "/home/marcos1701/Escritorio/Marcos.M/PSI/PSI/P3/chesstournament/manage.py",
  },
});