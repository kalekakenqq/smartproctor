<template>
  <div class="container">
    <h2>Дашборд преподавателя</h2>
    <div v-for="t in tests" :key="t.id" class="card">
      <strong>{{ t.title }}</strong>
      <p>{{ t.description }}</p>
      <router-link class="btn" :to="`/dashboard/tests/${t.id}/report`">Открыть отчёт</router-link>
    </div>
    <p v-if="tests.length === 0">У вас пока нет тестов</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const tests = ref([]);

onMounted(async () => {
  const { data } = await api.get("/tests");
  tests.value = data;
});
</script>
