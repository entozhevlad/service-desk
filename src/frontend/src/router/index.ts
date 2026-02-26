import { createRouter, createWebHistory } from "vue-router";
import TicketListView from "../views/TicketListView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [{ path: "/", name: "tickets", component: TicketListView }],
});
