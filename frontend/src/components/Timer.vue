<template>
  <div class="timer" :class="{ warning: remainingSeconds < 60 }">
    {{ formatted }}
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  durationMinutes: { type: Number, required: true },
});
const emit = defineEmits(["timeout"]);

const remainingSeconds = ref(props.durationMinutes * 60);
let intervalId = null;

const formatted = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60);
  const s = remainingSeconds.value % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

onMounted(() => {
  intervalId = setInterval(() => {
    if (remainingSeconds.value <= 0) {
      clearInterval(intervalId);
      emit("timeout");
      return;
    }
    remainingSeconds.value -= 1;
  }, 1000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});

defineExpose({ remainingSeconds });
</script>

<style scoped>
.timer {
  font-size: 28px;
  font-weight: 700;
  font-family: monospace;
}
.timer.warning {
  color: #dc2626;
}
</style>
