/**
 * Centralized API configuration for the Synestra client application.
 * All base URLs are standardized here to ensure they point to `/api` correctly.
 */

// Retrieve user environment overrides
const envApiUrl = import.meta.env.VITE_AUTH_API_URL || import.meta.env.VITE_API_URL;
const envChordsUrl = import.meta.env.VITE_CHORDS_API_URL;
const envStemsUrl = import.meta.env.VITE_STEMS_API_URL;
const envWsUrl = import.meta.env.VITE_BACKEND_WS_URL;
const envPlannerUrl = import.meta.env.VITE_PLANNER_API_URL;

// Helper to standardize a base URL ending with '/api'
// If no URL is provided, returns "/api" as a relative path to support local Vite proxy.
const standardizeApiUrl = (url?: string): string => {
  if (!url) {
    return "/api";
  }
  const base = url.replace(/\/+$/, "");
  return base.endsWith("/api") ? base : `${base}/api`;
};

// 1. Centralized HTTP API base URL (standardized to end with '/api')
export const API_BASE_URL = standardizeApiUrl(envApiUrl);

// 2. Specific overrides if configured, falling back to relative proxy path "/api"
export const CHORDS_API_BASE = envChordsUrl ? standardizeApiUrl(envChordsUrl) : "/api";
export const STEMS_API_BASE = envStemsUrl ? standardizeApiUrl(envStemsUrl) : "/api";

// 3. Centralized WebSocket base URL (standardized to start with ws:// or wss:// and end with /api)
export const WS_BASE_URL = (() => {
  if (envWsUrl) {
    return envWsUrl.replace(/\/+$/, "");
  }
  // Standardize the protocol and use CHORDS_API_BASE as base URL host/port/path
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const base = CHORDS_API_BASE;
  if (base.startsWith("/")) {
    // If CHORDS_API_BASE is a relative path (e.g. "/api"), resolve against local uvicorn host
    return `${wsProtocol}//127.0.0.1:8000${base}`;
  }
  const apiHost = base.replace(/^https?:\/\//, "");
  return `${wsProtocol}//${apiHost}`;
})();

// 4. Centralized Planner API base URL
export const PLANNER_API_BASE_URL = (envPlannerUrl || "http://127.0.0.1:8001").replace(/\/+$/, "");

/**
 * Resolves a relative path robustly against a base API URL configuration.
 * If the configured base URL is a relative path (starts with "/"), it resolves against window.location.origin.
 */
export const resolveAbsoluteUrl = (path: string, base: string): string => {
  const absoluteBase = (base && /^https?:\/\//i.test(base)) ? base : window.location.origin;
  return new URL(path, absoluteBase).toString();
};

/**
 * Joins a base API URL with a path, de-duplicating an overlapping
 * trailing/leading segment (e.g. avoids base=".../api" + path="/api/x" -> ".../api/api/x").
 */
export function joinApiUrl(base: string, path: string): string {
    if (/^https?:\/\//i.test(path)) return path; // already absolute

    const cleanBase = base.replace(/\/+$/, "");
    const cleanPath = path.replace(/^\/+/, "");

    const baseSegments = cleanBase.split("/");
    const lastBaseSegment = baseSegments[baseSegments.length - 1];
    const pathSegments = cleanPath.split("/");

    if (lastBaseSegment && pathSegments[0] === lastBaseSegment) {
        pathSegments.shift();
    }

    return `${cleanBase}/${pathSegments.join("/")}`;
}
