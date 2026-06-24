<template>
  <div class="container">
    <div v-if="auth.isTeacher" class="card">
      <h3>Создать тест</h3>
      <p v-if="error" class="error">{{ error }}</p>
      <form @submit.prevent="createTest">
        <label>Название</label>
        <input v-model="form.title" required />
        <label>Описание</label>
        <textarea v-model="form.description" rows="2"></textarea>
        <label>Длительность (мин)</label>
        <input v-model.number="form.duration_minutes" type="number" min="1" required />
        <label>Порог Risk Score для блокировки</label>
        <input v-model.number="form.risk_threshold" type="number" min="1" required />

        <div v-for="(q, idx) in form.questions" :key="idx" class="card" style="background: #f9fafb">
          <label>Вопрос {{ idx + 1 }}</label>
          <input v-model="q.text" placeholder="Текст вопроса" required />
          <div v-for="(opt, oi) in q.options" :key="oi" style="display: flex; gap: 8px; align-items: center">
            <input v-model="q.options[oi]" placeholder="Вариант ответа" required />
            <label style="display: flex; align-items: center; gap: 4px; white-space: nowrap; margin-bottom: 12px">
              <input type="radio" :name="'correct-' + idx" :checked="q.correct_index === oi" @change="q.correct_index = oi" style="width: auto" />
              верный
            </label>
          </div>
          <button type="button" class="btn secondary" @click="addOption(q)">+ вариант</button>
          <button type="button" class="btn secondary" @click="removeQuestion(idx)" style="margin-left: 8px">Удалить вопрос</button>
        </div>

        <button type="button" class="btn secondary" @click="addQuestion">+ вопрос</button>
        <br /><br />
        <button class="btn" type="submit" :disabled="loading">Создать тест</button>
      </form>
    </div>

    <div class="card">
      <h3>{{ auth.isTeacher ? "Мои тесты" : "Доступные тесты" }}</h3>
      <div v-for="t in tests" :key="t.id" class="card" style="background: #f9fafb">
        <strong>{{ t.title }}</strong>
        <p>{{ t.description }}</p>
        <p>Длительность: {{ t.duration_minutes }} мин · Порог риска: {{ t.risk_threshold }}</p>
        <router-link v-if="auth.isStudent" class="btn" :to="`/tests/${t.id}/exam`">Начать тест</router-link>
        <router-link v-else class="btn secondary" :to="`/dashboard/tests/${t.id}/report`">Отчёт</router-link>
      </div>
      <p v-if="tests.length === 0">Пока нет тестов</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../api";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const tests = ref([]);
const error = ref("");
const loading = ref(false);

const form = reactive({
  title: "",
  description: "",
  duration_minutes: 30,
  risk_threshold: 10,
  questions: [{ text: "", options: ["", ""], correct_index: 0 }],
});

function addQuestion() {
  form.questions.push({ text: "", options: ["", ""], correct_index: 0 });
}
function removeQuestion(idx) {
  form.questions.splice(idx, 1);
}
function addOption(q) {
  q.options.push("");
}

async function loadTests() {
  const { data } = await api.get("/tests");
  tests.value = data;
}

async function createTest() {
  error.value = "";
  loading.value = true;
  try {
    await api.post("/tests", form);
    form.title = "";
    form.description = "";
    form.questions = [{ text: "", options: ["", ""], correct_index: 0 }];
    await loadTests();
  } catch (e) {
    error.value = e.response?.data?.detail || "Не удалось создать тест";
  } finally {
    loading.value = false;
  }
}

onMounted(loadTests);
</script>
