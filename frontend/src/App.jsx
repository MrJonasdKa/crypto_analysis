import { useState } from 'react';
import { TickerTape } from './components/TickerTape';
import { Controls } from './components/Controls';
import { PriceChart } from './components/PriceChart';
import { PredictionCard } from './components/PredictionCard';
import { CorrelationHeatmap } from './components/CorrelationHeatmap';
import { useCoinData, useCorrelation } from './hooks/useCoinData';
import { useLatestPrices } from './hooks/useLatestPrices';
import './App.css';

export default function App() {
  const [symbol, setSymbol] = useState('BTC');
  const [days, setDays] = useState(90);

  const { prices, trend, feature, loading, error } = useCoinData(symbol, days);
  const { matrix, loading: corrLoading } = useCorrelation(days);
  const latestPrices = useLatestPrices();

  return (
    <div className="app">
      <TickerTape latestPrices={latestPrices} />

      <header className="app__header">
        <h1 className="app__title">Crypto Trend Terminal</h1>
        <p className="app__subtitle">
          Historical trend and short-horizon estimates across BTC, ETH, SOL, BNB
        </p>
      </header>

      <Controls
        selectedCoin={symbol}
        onSelectCoin={setSymbol}
        days={days}
        onSelectDays={setDays}
      />

      <main className="app__main">
        {error && <div className="app__error">Couldn't load data: {error}</div>}

        <PriceChart symbol={symbol} prices={prices} trend={trend} loading={loading} />

        <div className="app__row">
          <PredictionCard symbol={symbol} feature={feature} loading={loading} />
          <CorrelationHeatmap matrix={matrix} loading={corrLoading} />
        </div>
      </main>
    </div>
  );
}
