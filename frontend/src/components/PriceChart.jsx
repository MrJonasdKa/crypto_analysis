import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { coinColor } from '../lib/coins';
import './PriceChart.css';

function buildTrendSeries(prices, trend) {
  if (!trend) return prices;
  const n = prices.length;
  return prices.map((p, i) => ({
    ...p,
    trend_price: trend.intercept + trend.slope * i,
  }));
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date mono">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="chart-tooltip__row">
          <span className="chart-tooltip__label">{p.name}</span>
          <span className="mono">${p.value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
        </div>
      ))}
    </div>
  );
}

export function PriceChart({ symbol, prices, trend, loading }) {
  const color = coinColor(symbol);
  const data = buildTrendSeries(prices, trend);

  return (
    <div className="price-chart">
      <div className="price-chart__header">
        <div>
          <h2 className="price-chart__title">{symbol} price</h2>
          <p className="price-chart__subtitle">
            Dashed line is a {trend?.window_days ?? '—'}-day trend, not a forecast
          </p>
        </div>
        {trend && (
          <div className="price-chart__stat">
            <span className="price-chart__stat-label">R²</span>
            <span className="price-chart__stat-value mono">{trend.r_squared?.toFixed(3)}</span>
          </div>
        )}
      </div>

      <div className="price-chart__body">
        {loading ? (
          <div className="price-chart__loading">Loading…</div>
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
              <CartesianGrid stroke="var(--border-soft)" vertical={false} />
              <XAxis
                dataKey="price_date"
                tick={{ fill: 'var(--text-faint)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                axisLine={{ stroke: 'var(--border)' }}
                tickLine={false}
                minTickGap={40}
              />
              <YAxis
                tick={{ fill: 'var(--text-faint)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `$${v.toLocaleString()}`}
                width={70}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="close_price"
                name="Price"
                stroke={color}
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="linear"
                dataKey="trend_price"
                name="Trend"
                stroke="var(--text-muted)"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
