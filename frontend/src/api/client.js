/**
 * Typed fetch wrappers for all 8 Phase-2 API endpoints.
 * Error contract: throws { status, detail } on non-2xx responses.
 */

const BASE = import.meta.env.VITE_API_BASE ?? '';

async function apiFetch(path, retries = 1) {
  try {
    const res = await fetch(`${BASE}${path}`);
    if (!res.ok) {
      if (retries > 0 && res.status >= 500) {
        await new Promise((resolve) => setTimeout(resolve, 1200));
        return apiFetch(path, retries - 1);
      }
      let detail = `HTTP ${res.status}`;
      try { detail = (await res.json()).detail ?? detail; } catch {}
      const err = new Error(detail);
      err.status = res.status;
      err.detail = detail;
      throw err;
    }
    return res.json();
  } catch (err) {
    if (retries > 0 && !err.status) {
      await new Promise((resolve) => setTimeout(resolve, 1200));
      return apiFetch(path, retries - 1);
    }
    throw err;
  }
}

/** GET /api/health */
export function getHealth() {
  return apiFetch('/api/health');
}

/** GET /api/days → { days: string[], count: number } */
export function getDays() {
  return apiFetch('/api/days');
}

/**
 * GET /api/forecast
 * @param {string} date - YYYY-MM-DD
 * @param {string} cutoff - HH:MM
 */
export function getForecast(date, cutoff = '09:00') {
  return apiFetch(`/api/forecast?delivery_date=${date}&cutoff_time=${encodeURIComponent(cutoff)}`);
}

/**
 * GET /api/accuracy/summary
 * @param {string} [from] - YYYY-MM-DD
 * @param {string} [to]   - YYYY-MM-DD
 * @param {string} [cutoff] - HH:MM
 */
export function getAccuracySummary(from, to, cutoff = '09:00') {
  const p = buildWindowParams(from, to, cutoff);
  return apiFetch(`/api/accuracy/summary${p}`);
}

/** GET /api/accuracy/by-horizon */
export function getAccuracyByHorizon(from, to, cutoff = '09:00') {
  const p = buildWindowParams(from, to, cutoff);
  return apiFetch(`/api/accuracy/by-horizon${p}`);
}

/** GET /api/accuracy/by-hour */
export function getAccuracyByHour(from, to, cutoff = '09:00') {
  const p = buildWindowParams(from, to, cutoff);
  return apiFetch(`/api/accuracy/by-hour${p}`);
}

/**
 * GET /api/accuracy/distribution
 * @param {number} [bins=20]
 */
export function getDistribution(from, to, cutoff = '09:00', bins = 20) {
  const p = buildWindowParams(from, to, cutoff);
  return apiFetch(`/api/accuracy/distribution${p}&bins=${bins}`);
}

/**
 * Returns a pre-built download URL for the CSV export.
 * Use as <a href={getExportUrl(...)} download>.
 */
export function getExportUrl(from, to, cutoff = '09:00') {
  const p = buildWindowParams(from, to, cutoff);
  return `${BASE}/api/export/csv${p}`;
}

// ── helpers ──────────────────────────────────────────────────────────────────

function buildWindowParams(from, to, cutoff) {
  const params = new URLSearchParams();
  if (from) params.set('from_date', from);
  if (to)   params.set('to_date', to);
  if (cutoff) params.set('cutoff_time', cutoff);
  const str = params.toString();
  return str ? `?${str}` : '';
}
