<template>
  <div class="camera-box">
    <video ref="videoEl" autoplay playsinline muted class="video"></video>
    <canvas ref="canvasEl" class="hidden-canvas"></canvas>
    <div v-if="!ready" class="status">Запуск камеры…</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { FaceDetection } from "@mediapipe/face_detection";
import { Camera as MediaPipeCamera } from "@mediapipe/camera_utils";

const props = defineProps({
  startedAt: { type: Number, required: true }, // Date.now() ms when exam started
});
const emit = defineEmits(["violation"]);

const videoEl = ref(null);
const canvasEl = ref(null);
const ready = ref(false);

const YAW_THRESHOLD_DEGREES = 30;
const ABSENCE_FRAMES_THRESHOLD = 10; // ~consecutive frames with no face
const COOLDOWN_MS = 5000;

let faceDetection = null;
let camera = null;
let absentFrameCount = 0;
const lastEmittedAt = { face_absent: 0, face_away: 0, multiple_faces: 0 };

function elapsedSeconds() {
  return Math.floor((Date.now() - props.startedAt) / 1000);
}

function captureSnapshot() {
  const video = videoEl.value;
  const canvas = canvasEl.value;
  if (!video || !canvas || !video.videoWidth) return null;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.6);
}

function tryEmit(type) {
  const now = Date.now();
  if (now - lastEmittedAt[type] < COOLDOWN_MS) return;
  lastEmittedAt[type] = now;
  emit("violation", {
    type,
    elapsedSeconds: elapsedSeconds(),
    snapshotBase64: captureSnapshot(),
  });
}

function estimateYawDegrees(keypoints) {
  // mediapipe face_detection keypoints order: rightEye, leftEye, noseTip, mouthCenter, rightEarTragion, leftEarTragion
  const rightEye = keypoints[0];
  const leftEye = keypoints[1];
  const noseTip = keypoints[2];
  const midX = (rightEye.x + leftEye.x) / 2;
  const eyeDist = Math.abs(leftEye.x - rightEye.x);
  if (eyeDist === 0) return 0;
  const noseOffset = noseTip.x - midX;
  const ratio = noseOffset / (eyeDist / 2);
  return ratio * 45; // heuristic scale to degrees
}

function onResults(results) {
  ready.value = true;
  const detections = results.detections || [];

  if (detections.length === 0) {
    absentFrameCount += 1;
    if (absentFrameCount >= ABSENCE_FRAMES_THRESHOLD) {
      tryEmit("face_absent");
    }
    return;
  }
  absentFrameCount = 0;

  if (detections.length > 1) {
    tryEmit("multiple_faces");
  }

  const yaw = estimateYawDegrees(detections[0].landmarks);
  if (Math.abs(yaw) > YAW_THRESHOLD_DEGREES) {
    tryEmit("face_away");
  }
}

onMounted(async () => {
  faceDetection = new FaceDetection({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`,
  });
  faceDetection.setOptions({ model: "short", minDetectionConfidence: 0.5 });
  faceDetection.onResults(onResults);

  camera = new MediaPipeCamera(videoEl.value, {
    onFrame: async () => {
      await faceDetection.send({ image: videoEl.value });
    },
    width: 640,
    height: 480,
  });
  await camera.start();
});

onUnmounted(() => {
  if (camera) camera.stop();
  if (faceDetection) faceDetection.close();
});
</script>

<style scoped>
.camera-box {
  position: relative;
  width: 320px;
  border-radius: 10px;
  overflow: hidden;
  background: #000;
}
.video {
  width: 100%;
  display: block;
  transform: scaleX(-1);
}
.hidden-canvas {
  display: none;
}
.status {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 13px;
}
</style>
