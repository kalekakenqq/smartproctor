<template>
  <div class="container" style="max-width: 400px">
    <div class="card">
      <h2>Вход</h2>
      <p v-if="error" class="error">{{ error }}</p>
      <form @submit.prevent="submit">
        <label>Email</label>
        <input v-model="email" type="email" required />
        <label>Пароль</label>
        <input v-model="password" type="password" required />
        <button class="btn" type="submit" :disabled="loading">Войти</button>
      </form>
      <p style="margin-top: 12px">
        Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const auth = useAuthStore();
const router = useRouter();

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login({ email: email.value, password: password.value });
    router.push("/tests");
  } catch (e) {
    error.value = e.response?.data?.detail || "Ошибка входа";
  } finally {
    loading.value = false;
  }
}
</script>
