import { defineStore } from "pinia";
import api from "../api";
import { useAuthStore } from "./auth";

export const useExamStore = defineStore("exam", {
  state: () => ({
    test: null,
    session: null,
    answers: {},
    riskScore: 0,
    violations: [],
    blocked: false,
    socket: null,
  }),
  actions: {
    async loadTest(testId) {
      const { data } = await api.get(`/tests/${testId}`);
      this.test = data;
    },
    async startSession(testId) {
      const { data } = await api.post("/sessions", { test_id: testId });
      this.session = data;
      this.riskScore = data.risk_score;
      this.blocked = data.status === "blocked";
      return data;
    },
    selectAnswer(questionId, optionIndex) {
      this.answers[questionId] = optionIndex;
    },
    async finishSession() {
      const { data } = await api.post(`/sessions/${this.session.id}/finish`, { answers: this.answers });
      this.session = data;
      return data;
    },
    async reportViolation({ type, elapsedSeconds, snapshotBase64 }) {
      const { data } = await api.post("/violations", {
        session_id: this.session.id,
        type,
        elapsed_seconds: elapsedSeconds,
        snapshot_base64: snapshotBase64 || null,
      });
      this.violations.push(data);
      return data;
    },
    connectWebSocket() {
      const auth = useAuthStore();
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${protocol}://${window.location.host}/ws/sessions/${this.session.id}?token=${auth.token}`;
      this.socket = new WebSocket(url);
      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "risk_update") {
          this.riskScore = message.risk_score;
          if (message.blocked) {
            this.blocked = true;
          }
        }
      };
    },
    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    },
    reset() {
      this.test = null;
      this.session = null;
      this.answers = {};
      this.riskScore = 0;
      this.violations = [];
      this.blocked = false;
      this.disconnectWebSocket();
    },
  },
});
