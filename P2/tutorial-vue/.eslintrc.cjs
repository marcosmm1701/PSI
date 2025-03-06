/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  env: {
    node: true,
    browser: true,
    es2021: true,
  },

  globals: {
    Cypress: true,
  },

  root: true,
  extends: [
    "plugin:vue/vue3-recommended",
    "plugin:vue/vue3-essential",
    "eslint:recommended",
    "@vue/eslint-config-prettier",
  ],

  rules: {
    "vue/no-unused-vars": "error",
  },

  overrides: [
    {
      files: [
        "**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}",
        "cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}",
      ],
      extends: ["plugin:cypress/recommended"],
    },
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },
};
