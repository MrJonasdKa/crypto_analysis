import { useEffect, useState } from 'react';
import { api } from '../lib/api';

export function useCoinData(symbol, days) {
  const [state, setState] = useState({
    loading: true,
    error: null,
    prices: [],
    trend: null,
    feature: null,
  });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    Promise.all([
      api.getPrices(symbol, days),
      api.getTrendRegression(symbol, false),
      api.getFeatureRegression(symbol),
    ])
      .then(([pricesRes, trend, feature]) => {
        if (cancelled) return;
        setState({
          loading: false,
          error: null,
          prices: pricesRes.data,
          trend,
          feature,
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setState((s) => ({ ...s, loading: false, error: err.message }));
      });

    return () => {
      cancelled = true;
    };
  }, [symbol, days]);

  return state;
}

export function useCorrelation(days) {
  const [state, setState] = useState({ loading: true, error: null, matrix: {} });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true }));

    api
      .getCorrelation(days)
      .then((res) => {
        if (cancelled) return;
        setState({ loading: false, error: null, matrix: res.matrix });
      })
      .catch((err) => {
        if (cancelled) return;
        setState((s) => ({ ...s, loading: false, error: err.message }));
      });

    return () => {
      cancelled = true;
    };
  }, [days]);

  return state;
}
