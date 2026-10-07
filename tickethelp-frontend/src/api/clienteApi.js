import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
try {
  new URL(BASE_URL)
} catch {
  throw new Error(`VITE_API_URL invalida: "${BASE_URL}". Debe ser una URL completa (ej. https://api.midominio.com).`)
}

const clienteApi = axios.create({
  baseURL: `${BASE_URL}/api`,
});

clienteApi.interceptors.request.use(
  (config) => {
    // Buscar el token CORRECTO
    const token =
      sessionStorage.getItem("access") ||
      localStorage.getItem("access");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

clienteApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && window.location.pathname !== "/auth/login") {
      localStorage.removeItem("access");
      sessionStorage.removeItem("access");
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  }
);

export default clienteApi;
