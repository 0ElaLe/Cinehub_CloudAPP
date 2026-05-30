// En producción (mismo origen), VITE_API_BASE_URL="" → rutas relativas.
// En desarrollo, si no está definida, usa el backend local.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("cinehub_token");
}

function authHeaders(extra = {}) {
  const token = getToken();
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function parseJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  let payload = null;

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    const detail = payload?.detail || payload || `Error HTTP ${response.status}`;
    throw new Error(detail);
  }

  return payload;
}

export async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  return parseJsonResponse(response);
}

export async function getMe() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: authHeaders(),
  });

  return parseJsonResponse(response);
}

export async function getProjects() {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    headers: authHeaders(),
  });

  return parseJsonResponse(response);
}

export async function getProjectMaterials(projectId) {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/materials`, {
    headers: authHeaders(),
  });

  return parseJsonResponse(response);
}

export async function uploadMaterial(projectId, payload) {
  const formData = new FormData();
  formData.append("file", payload.file);
  formData.append("tipo_material", payload.tipo_material);
  formData.append("version", payload.version);
  formData.append("container_name", payload.container_name);
  formData.append("nivel_confidencialidad", payload.nivel_confidencialidad);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/materials`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  return parseJsonResponse(response);
}

export async function downloadMaterial(material) {
  const response = await fetch(`${API_BASE_URL}/materials/${material.material_id}/download`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail || `Error HTTP ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = material.nombre || `material-${material.material_id}`;
  document.body.appendChild(link);
  link.click();

  link.remove();
  window.URL.revokeObjectURL(url);
}

export { API_BASE_URL };
