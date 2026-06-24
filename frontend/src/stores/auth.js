import { defineStore } from "pinia";
import axios from "axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("sp_token") || null,
    user: JSON.parse(localStorage.getItem("sp_user") || "null"),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isTeacher: (state) => state.user?.role === "teacher",
    isStudent: (state) => state.user?.role === "student",
  },
  actions: {
    async register({ email, password, full_name, role }) {
      const { data } = await axios.post("/auth/register", { email, password, full_name, role });
      this.setSession(data);
    },
    async login({ email, password }) {
      const { data } = await axios.post("/auth/login", { email, password });
      this.setSession(data);
    },
    setSession(data) {
      this.token = data.access_token;
      this.user = data.user;
      localStorage.setItem("sp_token", data.access_token);
      localStorage.setItem("sp_user", JSON.stringify(data.user));
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("sp_token");
      localStorage.removeItem("sp_user");
    },
  },
});
