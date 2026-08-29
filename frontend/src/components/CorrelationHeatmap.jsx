import { COINS } from '../lib/coins';
import './CorrelationHeatmap.css';

function cellColor(value) {
  // value ranges -1..1. Map to an intensity of the app's neutral accent.
  const intensity = Math.abs(value);
  const alpha = 0.12 + intensity * 0.55;
  return value >= 0
    ? `rgba(20, 241, 149, ${alpha})` // var(--up)
    : `rgba(247, 67, 79, ${alpha})`; // var(--down)
}

export function CorrelationHeatmap({ matrix, loading }) {
  const symbols = COINS.map((c) => c.symbol);

  return (
    <div className="correlation-card">
      <div className="correlation-card__eyebrow">Correlation</div>

      {loading || !matrix || Object.keys(matrix).length === 0 ? (
        <div className="correlation-card__loading">Loading…</div>
      ) : (
        <div className="heatmap" style={{ '--n': symbols.length }}>
          <div className="heatmap__corner" />
          {symbols.map((s) => (
            <div key={`col-${s}`} className="heatmap__label heatmap__label--col mono">
              {s}
            </div>
          ))}

          {symbols.map((rowSym) => (
            <>
              <div key={`row-${rowSym}`} className="heatmap__label heatmap__label--row mono">
                {rowSym}
              </div>
              {symbols.map((colSym) => {
                const value = matrix[rowSym]?.[colSym] ?? null;
                return (
                  <div
                    key={`${rowSym}-${colSym}`}
                    className="heatmap__cell mono"
                    style={{ background: value != null ? cellColor(value) : 'transparent' }}
                    title={`${rowSym} × ${colSym}: ${value?.toFixed(2) ?? '—'}`}
                  >
                    {value != null ? value.toFixed(2) : '—'}
                  </div>
                );
              })}
            </>
          ))}
        </div>
      )}
    </div>
  );
}
