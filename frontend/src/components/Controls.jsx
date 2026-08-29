import { COINS } from '../lib/coins';
import './Controls.css';

const RANGES = [30, 90, 180];

export function Controls({ selectedCoin, onSelectCoin, days, onSelectDays }) {
  return (
    <div className="controls">
      <div className="controls__coins" role="tablist" aria-label="Select coin">
        {COINS.map((coin) => {
          const active = coin.symbol === selectedCoin;
          return (
            <button
              key={coin.symbol}
              role="tab"
              aria-selected={active}
              className={`coin-tab ${active ? 'is-active' : ''}`}
              style={active ? { '--tab-color': coin.color } : undefined}
              onClick={() => onSelectCoin(coin.symbol)}
            >
              {coin.symbol}
            </button>
          );
        })}
      </div>

      <div className="controls__range" role="group" aria-label="Days range">
        {RANGES.map((r) => (
          <button
            key={r}
            className={`range-btn ${r === days ? 'is-active' : ''}`}
            onClick={() => onSelectDays(r)}
          >
            {r}D
          </button>
        ))}
      </div>
    </div>
  );
}
