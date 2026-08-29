import { coinColor } from '../lib/coins';
import './PredictionCard.css';

export function PredictionCard({ symbol, feature, loading }) {
  const color = coinColor(symbol);

  return (
    <div className="prediction-card">
      <div className="prediction-card__eyebrow" style={{ color }}>
        Short-horizon estimate
      </div>

      {loading || !feature ? (
        <div className="prediction-card__loading">Loading…</div>
      ) : (
        <>
          <div className="prediction-card__value mono">
            ${feature.predicted_price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
          <div className="prediction-card__meta">
            {feature.horizon_days}-day estimate · R² {feature.r_squared?.toFixed(3)}
          </div>
          <p className="prediction-card__disclaimer">
            Experimental regression on volatility, moving averages, and volume — not financial
            advice and not a reliable trading signal.
          </p>
        </>
      )}
    </div>
  );
}
