const API_BASE = "http://127.0.0.1:8000/api";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_) {
      // response had no JSON body
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

const Api = {
  getApplications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/applications${query ? `?${query}` : ""}`);
  },
  getStats() {
    return apiRequest("/applications/stats");
  },
  createApplication(data) {
    return apiRequest("/applications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  },
  updateApplication(id, data) {
    return apiRequest(`/applications/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  },
  deleteApplication(id) {
    return apiRequest(`/applications/${id}`, { method: "DELETE" });
  },
  analyzeResume(file) {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest("/resume/analyze", { method: "POST", body: formData });
  },
  matchJob(file, jobDescription) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);
    return apiRequest("/resume/match", { method: "POST", body: formData });
  },
  getDocuments() {
    return apiRequest("/documents");
  },
  uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest("/documents", { method: "POST", body: formData });
  },
  deleteDocument(id) {
    return apiRequest(`/documents/${id}`, { method: "DELETE" });
  },
  askAssistant(question) {
    return apiRequest("/assistant/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  },
};
