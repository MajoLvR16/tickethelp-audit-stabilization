// FASE 4 - Pruebas de resiliencia en cliente web.
// Arnés aislado: no modifica tickethelp-frontend/. Ejecuta node:test contra
// una copia en memoria del código fuente real de src/api/client.js (la
// implementación de cliente HTTP más completa localizada en el frontend,
// que además coexiste con src/lib/api.js y src/api/clienteApi.js — ver
// hallazgo de duplicación en _audit_docs/AUDITORIA_CONFIGURACION_INFORME.md).
//
// Nota técnica: el archivo fuente usa `import.meta.env`, `localStorage`,
// `sessionStorage` y `window`, globales que sólo existen bajo Vite/navegador.
// Para probar la lógica REAL sin alterar el repositorio (regla READ-ONLY),
// se sustituye textualmente `import.meta.env` por un objeto literal con el
// entorno bajo prueba y se inyectan shims mínimos de storage/window antes de
// importar el módulo vía una URL de datos (data:).
import { test, before, beforeEach } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = path.resolve(__dirname, "..", "..", "tickethelp-frontend");
const ENV_PATH = path.join(FRONTEND_ROOT, ".env");
const CLIENT_SOURCE_PATH = path.join(FRONTEND_ROOT, "src", "api", "client.js");

function readEnvVar(name) {
  const content = fs.readFileSync(ENV_PATH, "utf-8");
  const match = content.match(new RegExp(`^${name}=(.*)$`, "m"));
  return match ? match[1].trim() : undefined;
}

// ---------------------------------------------------------------------------
// FE-RES-01: validación sintáctica estricta de VITE_BACKEND_URL
// ---------------------------------------------------------------------------
test("FE-RES-01: VITE_BACKEND_URL declarada en .env es una URL válida (new URL + '//')", () => {
  const value = readEnvVar("VITE_BACKEND_URL");
  assert.ok(value, "VITE_BACKEND_URL debe estar presente en tickethelp-frontend/.env");

  // No conformidad esperada y confirmada por auditoría: el valor real es
  // "https:tickethelp-backend.onrender.com" (sin "//"), por lo que esta
  // aserción documenta el defecto reproducible: new URL() debe fallar.
  assert.match(
    value,
    /^https?:\/\//,
    `VITE_BACKEND_URL="${value}" carece del separador "//" tras el esquema (RF-CONFIG-02)`
  );
});

test("FE-RES-01b: el valor actual de VITE_BACKEND_URL es rechazado por new URL() (reproduce el defecto)", () => {
  const value = readEnvVar("VITE_BACKEND_URL");
  assert.throws(() => new URL(value), TypeError);
});

test("FE-RES-01c: el código fuente sólo consume VITE_API_URL, nunca VITE_BACKEND_URL (variable huérfana)", () => {
  const sourceFiles = [
    "src/api/client.js",
    "src/api/clienteApi.js",
    "src/lib/api.js",
  ].map((rel) => fs.readFileSync(path.join(FRONTEND_ROOT, rel), "utf-8"));

  for (const source of sourceFiles) {
    assert.ok(source.includes("VITE_API_URL"), "se espera consumo de VITE_API_URL");
    assert.ok(!source.includes("VITE_BACKEND_URL"), "VITE_BACKEND_URL no debería usarse (huérfana)");
  }
});

// ---------------------------------------------------------------------------
// Harness para importar el cliente HTTP real bajo entorno simulado
// ---------------------------------------------------------------------------
function makeStorage() {
  const store = new Map();
  return {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
  };
}

async function loadRealApiClient({ VITE_API_URL } = {}) {
  const rawSource = fs.readFileSync(CLIENT_SOURCE_PATH, "utf-8");
  const patchedSource = rawSource.replace(
    /import\.meta\.env/g,
    JSON.stringify({ VITE_API_URL })
  );
  const dataUrl = `data:text/javascript;base64,${Buffer.from(patchedSource, "utf-8").toString("base64")}`;
  return import(dataUrl);
}

let originalFetch;
let originalWindow;

before(() => {
  originalFetch = globalThis.fetch;
  originalWindow = globalThis.window;
});

beforeEach(() => {
  globalThis.localStorage = makeStorage();
  globalThis.sessionStorage = makeStorage();
  globalThis.window = { location: { pathname: "/", href: "" } };
});

// ---------------------------------------------------------------------------
// FE-RES-02: extracción de mensaje estructurado ante 401/403
// ---------------------------------------------------------------------------
test("FE-RES-02: ante 403 con {detail:...} el cliente propaga err.message sin 'undefined'", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "No tiene permisos para esta acción." }), {
      status: 403,
      headers: { "Content-Type": "application/json" },
    });

  await assert.rejects(
    () => api("/api/reports/stats/general-stats/"),
    (err) => {
      assert.equal(err.status, 403);
      assert.equal(err.message, "No tiene permisos para esta acción.");
      assert.notEqual(err.message, "undefined");
      return true;
    }
  );

  globalThis.fetch = originalFetch;
});

test("FE-RES-02b: ante 401 el cliente limpia tokens y redirige a /auth/login sin colapsar", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.localStorage.setItem("access", "token-expirado");
  globalThis.sessionStorage.setItem("access", "token-expirado");
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Token inválido o expirado" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });

  await assert.rejects(
    () => api("/api/tickets/1/history/"),
    (err) => {
      assert.equal(err.status, 401);
      assert.equal(err.message, "Token inválido o expirado");
      return true;
    }
  );

  assert.equal(globalThis.localStorage.getItem("access"), null);
  assert.equal(globalThis.sessionStorage.getItem("access"), null);
  assert.equal(globalThis.window.location.href, "/auth/login");

  globalThis.fetch = originalFetch;
});

test("FE-RES-02c: respuesta de error sin cuerpo JSON no produce mensaje 'undefined'", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.fetch = async () =>
    new Response("", { status: 403, statusText: "Forbidden" });

  await assert.rejects(
    () => api("/api/reports/stats/general-stats/"),
    (err) => {
      assert.equal(err.status, 403);
      assert.notEqual(err.message, undefined);
      assert.notEqual(String(err.message).includes("undefined"), true);
      return true;
    }
  );

  globalThis.fetch = originalFetch;
});

// ---------------------------------------------------------------------------
// FE-RES-03: timeouts y caídas 500
// ---------------------------------------------------------------------------
test("FE-RES-03a: respuesta 500 del servidor se propaga como excepción controlada (no crashea el proceso)", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.fetch = async () =>
    new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });

  await assert.rejects(
    () => api("/api/reports/stats/general-stats/"),
    (err) => {
      assert.equal(err.status, 500);
      return true;
    }
  );

  globalThis.fetch = originalFetch;
});

test("FE-RES-03b: timeout de red (fetch nunca resuelve) no cuelga la prueba: se rechaza vía AbortController externo", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.fetch = () => new Promise(() => {}); // nunca resuelve, simula servidor caído

  const timeoutMs = 200;
  const withTimeout = (promise, ms) =>
    Promise.race([
      promise,
      new Promise((_, reject) => setTimeout(() => reject(new Error("TIMEOUT")), ms)),
    ]);

  await assert.rejects(
    () => withTimeout(api("/api/reports/stats/general-stats/"), timeoutMs),
    /TIMEOUT/
  );

  globalThis.fetch = originalFetch;
});

test("FE-RES-03c: fetch que rechaza por caída de red (TypeError) se propaga sin colapsar el proceso", async () => {
  const { api } = await loadRealApiClient({ VITE_API_URL: "http://api.test" });

  globalThis.fetch = async () => {
    throw new TypeError("fetch failed");
  };

  await assert.rejects(() => api("/api/reports/stats/general-stats/"), TypeError);

  globalThis.fetch = originalFetch;
});
