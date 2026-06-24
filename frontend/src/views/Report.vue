<template>
  <div class="container">
    <h2>Отчёт по тесту</h2>

    <div class="card">
      <h3>Распределение баллов по группе</h3>
      <canvas ref="scoresChartEl" height="120"></canvas>
    </div>

    <div class="card">
      <h3>Нарушения по минутам теста</h3>
      <canvas ref="heatmapChartEl" height="120"></canvas>
    </div>

    <div class="card">
      <h3>Сравнение студентов</h3>
      <table style="width: 100%; border-collapse: collapse">
        <thead>
          <tr style="text-align: left; border-bottom: 1px solid #e5e7eb">
            <th>Студент</th>
            <th>Балл</th>
            <th>Risk Score</th>
            <th>Статус</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in scores" :key="s.session_id" style="border-bottom: 1px solid #f3f4f6">
            <td>{{ s.student_name }}</td>
            <td>{{ s.score }}%</td>
            <td>{{ s.risk_score }}</td>
            <td>{{ s.status }}</td>
            <td><button class="btn secondary" @click="openSessionReport(s.session_id)">Снимки нарушений</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selectedViolations" class="card">
      <h3>Нарушения сессии #{{ selectedSessionId }}</h3>
      <div v-for="v in selectedViolations" :key="v.id" class="card" style="background: #f9fafb">
        <p>{{ v.type }} · {{ v.elapsed_seconds }}с · вес {{ v.weight }}</p>
        <img v-if="v.snapshot_path" :src="v.snapshot_path" style="max-width: 200px; border-radius: 6px" />
      </div>
      <p v-if="selectedViolations.length === 0">Нарушений нет</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import Chart from "chart.js/auto";
import api from "../api";

const props = defineProps({ testId: { type: String, required: true } });

const scores = ref([]);
const heatmap = ref({});
const scoresChartEl = ref(null);
const heatmapChartEl = ref(null);
const selectedViolations = ref(null);
const selectedSessionId = ref(null);

async function openSessionReport(sessionId) {
  selectedSessionId.value = sessionId;
  const { data } = await api.get(`/reports/session/${sessionId}`);
  selectedViolations.value = data;
}

function renderScoresChart() {
  new Chart(scoresChartEl.value, {
    type: "bar",
    data: {
      labels: scores.value.map((s) => s.student_name),
      datasets: [{ label: "Балл (%)", data: scores.value.map((s) => s.score), backgroundColor: "#2563eb" }],
    },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } },
  });
}

function renderHeatmapChart() {
  const minutes = Object.keys(heatmap.value);
  const counts = Object.values(heatmap.value);
  new Chart(heatmapChartEl.value, {
    type: "bar",
    data: {
      labels: minutes.map((m) => `${m} мин`),
      datasets: [{ label: "Нарушений", data: counts, backgroundColor: "#dc2626" }],
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } },
  });
}

onMounted(async () => {
  const [scoresResp, heatmapResp] = await Promise.all([
    api.get(`/reports/test/${props.testId}/scores`),
    api.get(`/reports/test/${props.testId}/heatmap`),
  ]);
  scores.value = scoresResp.data;
  heatmap.value = heatmapResp.data;
  await nextTick();
  renderScoresChart();
  renderHeatmapChart();
});
</script>
