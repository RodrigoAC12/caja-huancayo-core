import api, { TOKEN_KEY, USER_KEY } from "./api";

export async function login(username, password) {
  const usuario = String(username || "").trim();

  const response = await api.post("/auth/login", {
    username: usuario,
    codigo_empleado: usuario,
    password: String(password || "")
  });

  const data = response.data;

  if (!data?.access_token) {
    throw new Error("No se recibió token de acceso.");
  }

  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user || {}));

  return data;
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.location.href = "/login";
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);

  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getToken());
}

const authService = {
  login,
  logout,
  getToken,
  getUser,
  isAuthenticated
};

export default authService;