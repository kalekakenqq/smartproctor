import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

import Login from "./views/Login.vue";
import Register from "./views/Register.vue";
import TestList from "./views/TestList.vue";
import TestExam from "./views/TestExam.vue";
import Dashboard from "./views/Dashboard.vue";
import Report from "./views/Report.vue";

const routes = [
  { path: "/", redirect: "/tests" },
  { path: "/login", component: Login, meta: { public: true } },
  { path: "/register", component: Register, meta: { public: true } },
  { path: "/tests", component: TestList },
  { path: "/tests/:testId/exam", component: TestExam, props: true },
  { path: "/dashboard", component: Dashboard, meta: { teacherOnly: true } },
  { path: "/dashboard/tests/:testId/report", component: Report, props: true, meta: { teacherOnly: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) {
    return "/login";
  }
  if (to.meta.teacherOnly && !auth.isTeacher) {
    return "/tests";
  }
  return true;
});

export default router;
