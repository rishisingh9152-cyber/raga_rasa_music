const rawApiBase = import.meta.env.VITE_API_BASE_URL;

// Production-safe fallback points to deployed backend (not localhost).
export const API_BASE_URL = (rawApiBase && rawApiBase.trim())
  ? rawApiBase.trim().replace(/\/$/, "")
  : "https://raga-rasa-backend-gopl.onrender.com/api";
