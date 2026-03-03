/**
 * API Service Layer
 * All backend communication goes through this module.
 */

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Create axios instance with defaults
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 300000, // 5 min for NLP processing (initial load)
});

// ─────────────────────────────────────────────
// CV Upload API
// ─────────────────────────────────────────────
export const uploadAPI = {
    uploadCV: (file, name, email = "") => {
        const form = new FormData();
        form.append("file", file);
        form.append("name", name);
        form.append("email", email);
        return api.post("/upload/cv", form, {
            headers: { "Content-Type": "multipart/form-data" },
        });
    },
    getCandidates: () => api.get("/upload/candidates"),
    getCandidate: (id) => api.get(`/upload/candidates/${id}`),
    deleteCandidate: (id) => api.delete(`/upload/candidates/${id}`),
};

// ─────────────────────────────────────────────
// Job Description API
// ─────────────────────────────────────────────
export const jobAPI = {
    createJob: (data) => api.post("/jobs/", data),
    getJobs: () => api.get("/jobs/"),
    getJob: (id) => api.get(`/jobs/${id}`),
    updateJob: (id, data) => api.put(`/jobs/${id}`, data),
    deleteJob: (id) => api.delete(`/jobs/${id}`),
};

// ─────────────────────────────────────────────
// Matching API
// ─────────────────────────────────────────────
export const matchAPI = {
    matchSingle: (candidateId, jobId) =>
        api.post("/match/single", { candidate_id: candidateId, job_id: jobId }),
    matchBulk: (jobId, candidateIds = null) =>
        api.post("/match/bulk", { job_id: jobId, candidate_ids: candidateIds }),
    getDashboardStats: () => api.get("/match/dashboard/stats"),
    downloadReport: (candidateId, jobId) =>
        api.get(`/match/report/${candidateId}/${jobId}`, { responseType: "blob" }),
};

export default api;
