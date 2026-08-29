const BASE_URL = 'http://localhost:8000';

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getCoins: () => get('/coins'),

  getPrices: (symbol, days = 90) => get(`/prices/${symbol}?days=${days}`),

  getTrendRegression: (symbol, useLog = false) =>
    get(`/regression/trend/${symbol}?use_log=${useLog}`),

  getFeatureRegression: (symbol) => get(`/regression/feature/${symbol}`),

  getCorrelation: (days = 90) => get(`/correlation?days=${days}`),
};
