<template>
  <nav class="topbar">
    <div>
      <router-link to="/tests">Тесты</router-link>
      <router-link v-if="auth.isTeacher" to="/dashboard">Дашборд</router-link>
    </div>
    <div v-if="auth.isAuthenticated">
      <span style="margin-right: 16px">{{ auth.user.full_name }} ({{ auth.user.role }})</span>
      <button class="btn secondary" @click="logout">Выйти</button>
    </div>
  </nav>
  <router-view />
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();
const router = useRouter();

function logout() {
  auth.logout();
  router.push("/login");
}
</script>
