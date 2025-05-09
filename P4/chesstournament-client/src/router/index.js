import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/Home_View.vue"),
    },
    {
      path: "/login",
      name: "loginView",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/Login_View.vue"),
    },
    {
      path: "/tournamentdetail/:id",
      name: "tournamentDetailView",
      component: () => import("../views/TournamentDetail.vue"),
    },
    {
      path: "/logout",
      name: "logout",
      component: () => import("../views/Logout_View.vue"),
    },
    {
      path: "/faq",
      name: "faq",
      component: () => import("../views/Faq_View.vue"),
    },

    {
      path: "/createtournament",
      name: "createTournament",
      component: () => import("../views/CreateTournament.vue"),
    },
  ],
});

export default router;
