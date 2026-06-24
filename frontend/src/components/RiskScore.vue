<template>
  <div class="risk-score" :class="level">
    <span>Risk Score: {{ score }} / {{ threshold }}</span>
    <div class="bar">
      <div class="bar-fill" :style="{ width: percentage + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  score: { type: Number, required: true },
  threshold: { type: Number, required: true },
});

const percentage = computed(() => Math.min(100, (props.score / props.threshold) * 100));
const level = computed(() => {
  if (percentage.value >= 100) return "critical";
  if (percentage.value >= 60) return "high";
  return "normal";
});
</script>

<style scoped>
.risk-score {
  font-weight: 600;
  margin-bottom: 8px;
}
.bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 6px;
}
.bar-fill {
  height: 100%;
  background: #22c55e;
  transition: width 0.3s ease;
}
.risk-score.high .bar-fill {
  background: #f59e0b;
}
.risk-score.critical .bar-fill {
  background: #dc2626;
}
.risk-score.critical {
  color: #dc2626;
}
</style>
