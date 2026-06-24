<template>
  <span class="badge" :class="violation.type">{{ label }}</span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  violation: { type: Object, required: true },
});

const LABELS = {
  face_absent: "Лицо не обнаружено",
  face_away: "Взгляд в сторону",
  multiple_faces: "Несколько лиц в кадре",
};

const label = computed(() => LABELS[props.violation.type] || props.violation.type);
</script>

<style scoped>
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}
.badge.face_absent {
  background: #f59e0b;
}
.badge.face_away {
  background: #3b82f6;
}
.badge.multiple_faces {
  background: #dc2626;
}
</style>
