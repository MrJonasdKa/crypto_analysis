import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { COINS, coinColor } from '../lib/coins';

export function useLatestPrices() {
  const [latest, setLatest] = useState({});

  useEffect(() => {
    let cancelled = false;

    Promise.all(
      COINS.map((coin) =>
        api.getPrices(coin.symbol, 2).then((res) => ({ symbol: coin.symbol, data: res.data }))
      )
    ).then((results) => {
      if (cancelled) return;
      const next = {};
      for (const { symbol, data } of results) {
        if (data.length === 0) continue;
        const last = data[data.length - 1];
        const prev = data.length > 1 ? data[data.length - 2] : last;
        const changePct = prev.close_price
          ? ((last.close_price - prev.close_price) / prev.close_price) * 100
          : 0;
        next[symbol] = { price: last.close_price, changePct, color: coinColor(symbol) };
      }
      setLatest(next);
    });

    return () => {
      cancelled = true;
    };
  }, []);

  return latest;
}
