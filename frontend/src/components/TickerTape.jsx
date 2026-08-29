import { COINS } from '../lib/coins';
import './TickerTape.css';

export function TickerTape({ latestPrices }) {
  // latestPrices: { BTC: { price, changePct }, ETH: {...}, ... }
  const items = COINS.map((coin) => {
    const data = latestPrices[coin.symbol];
    return { ...coin, ...data };
  });

  // duplicate the list so the scroll loop is seamless
  const track = [...items, ...items];

  return (
    <div className="ticker-tape" role="status" aria-label="Current prices">
      <div className="ticker-tape__track">
        {track.map((item, i) => (
          <span className="ticker-tape__item" key={`${item.symbol}-${i}`}>
            <span className="ticker-tape__dot" style={{ background: item.color }} />
            <span className="ticker-tape__symbol">{item.symbol}</span>
            {item.price != null ? (
              <>
                <span className="ticker-tape__price mono">
                  ${item.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </span>
                <span
                  className={`ticker-tape__change mono ${item.changePct >= 0 ? 'is-up' : 'is-down'}`}
                >
                  {item.changePct >= 0 ? '▲' : '▼'} {Math.abs(item.changePct).toFixed(2)}%
                </span>
              </>
            ) : (
              <span className="ticker-tape__price mono">—</span>
            )}
          </span>
        ))}
      </div>
    </div>
  );
}
