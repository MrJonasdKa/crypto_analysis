export const COINS = [
  { symbol: 'BTC', name: 'Bitcoin', color: 'var(--btc)' },
  { symbol: 'ETH', name: 'Ethereum', color: 'var(--eth)' },
  { symbol: 'SOL', name: 'Solana', color: 'var(--sol)' },
  { symbol: 'BNB', name: 'BNB', color: 'var(--bnb)' },
];

export const coinColor = (symbol) => {
  const found = COINS.find((c) => c.symbol === symbol);
  return found ? found.color : 'var(--text-muted)';
};
