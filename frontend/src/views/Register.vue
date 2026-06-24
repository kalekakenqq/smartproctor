<template>
  <div class="container" style="max-width: 400px">
    <div class="card">
      <h2>Регистрация</h2>
      <p v-if="error" class="error">{{ error }}</p>
      <form @submit.prevent="submit">
        <label>Имя</label>
        <input v-model="fullName" required />
        <label>Email</label>
        <input v-model="email" type="email" required />
        <label>Пароль</label>
        <input v-model="password" type="password" minlength="6" required />
        <label>Роль</label>
        <select v-model="role">
          <option value="student">Студент</option>
          <option value="teacher">Преподаватель</option>
        </select>
        <button class="btn" type="submit" :disabled="loading">Зарегистрироваться</button>
      </form>
      <p style="margin-top: 12px">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const fullName = ref("");
const email = ref("");
const password = ref("");
const role = ref("student");
const error = ref("");
const loading = ref(false);
const auth = useAuthStore();
const router = useRouter();

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.register({ email: email.value, password: password.value, full_name: fullName.value, role: role.value });
    router.push("/tests");
  } catch (e) {
    error.value = e.response?.data?.detail || "Ошибка регистрации";
  } finally {
    loading.value = false;
  }
}
</script>
