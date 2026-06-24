<template>
  <div class="container" v-if="exam.test && exam.session">
    <div v-if="exam.blocked" class="card" style="border: 2px solid #dc2626">
      <h2 style="color: #dc2626">Сессия заблокирована</h2>
      <p>Превышен допустимый порог Risk Score. Тест завершён принудительно.</p>
      <router-link class="btn" to="/tests">К списку тестов</router-link>
    </div>

    <div v-else-if="finished" class="card">
      <h2>Тест завершён</h2>
      <p>Ваш результат: {{ result.score }}%</p>
      <router-link class="btn" to="/tests">К списку тестов</router-link>
    </div>

    <div v-else style="display: flex; gap: 20px">
      <div style="flex: 1">
        <div class="card" style="display: flex; justify-content: space-between; align-items: center">
          <h2>{{ exam.test.title }}</h2>
          <Timer :duration-minutes="exam.test.duration_minutes" @timeout="submit" />
        </div>

        <div v-for="q in exam.test.questions" :key="q.id" class="card">
          <p><strong>{{ q.text }}</strong></p>
          <label v-for="(opt, idx) in q.options" :key="idx" style="display: flex; gap: 8px; align-items: center; font-weight: normal">
            <input
              type="radio"
              :name="'q-' + q.id"
              :value="idx"
              :checked="exam.answers[q.id] === idx"
              @change="exam.selectAnswer(q.id, idx)"
              style="width: auto; margin-bottom: 0"
            />
            {{ opt }}
          </label>
        </div>

        <button class="btn" @click="submit" :disabled="submitting">Завершить тест</button>
      </div>

      <div style="width: 320px">
        <div class="card">
          <RiskScore :score="exam.riskScore" :threshold="exam.test.risk_threshold" />
          <Camera :started-at="startedAt" @violation="onViolation" />
        </div>
        <div class="card">
          <h4>Нарушения</h4>
          <div v-for="v in exam.violations" :key="v.id" style="margin-bottom: 6px">
            <ViolationBadge :violation="v" />
          </div>
          <p v-if="exam.violations.length === 0" style="font-size: 13px; color: #6b7280">Нарушений не обнаружено</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useExamStore } from "../stores/exam";
import Timer from "../components/Timer.vue";
import RiskScore from "../components/RiskScore.vue";
import Camera from "../components/Camera.vue";
import ViolationBadge from "../components/ViolationBadge.vue";

const props = defineProps({ testId: { type: String, required: true } });

const exam = useExamStore();
const startedAt = ref(Date.now());
const finished = ref(false);
const submitting = ref(false);
const result = ref(null);

async function onViolation(payload) {
  await exam.reportViolation(payload);
}

async function submit() {
  if (finished.value || exam.blocked) return;
  submitting.value = true;
  try {
    result.value = await exam.finishSession();
    finished.value = true;
  } finally {
    submitting.value = false;
  }
}

watch(
  () => exam.blocked,
  (blocked) => {
    if (blocked) exam.disconnectWebSocket();
  }
);

onMounted(async () => {
  exam.reset();
  await exam.loadTest(props.testId);
  await exam.startSession(Number(props.testId));
  startedAt.value = Date.now();
  exam.connectWebSocket();
});

onUnmounted(() => {
  exam.disconnectWebSocket();
});
</script>
