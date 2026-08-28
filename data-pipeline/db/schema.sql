-- Crypto Data Analysis — schema.sql
-- Target: MySQL / MariaDB

CREATE DATABASE IF NOT EXISTS crypto_analysis
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE crypto_analysis;

-- ---------------------------------------------------------------
-- coins: static reference table for the assets we track
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coins (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    symbol       VARCHAR(10) NOT NULL UNIQUE,     -- BTC, ETH, SOL, BNB
    coingecko_id VARCHAR(50) NOT NULL UNIQUE,      -- bitcoin, ethereum, solana, binancecoin
    name         VARCHAR(50) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------
-- daily_prices: raw OHLCV pulled from CoinGecko, one row per coin/day
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_prices (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    coin_id     INT UNSIGNED NOT NULL,
    price_date  DATE NOT NULL,
    open_price  DECIMAL(20,8),
    high_price  DECIMAL(20,8),
    low_price   DECIMAL(20,8),
    close_price DECIMAL(20,8) NOT NULL,
    volume      DECIMAL(24,2),
    market_cap  DECIMAL(24,2),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_daily_prices_coin
        FOREIGN KEY (coin_id) REFERENCES coins(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_coin_date (coin_id, price_date),
    INDEX idx_price_date (price_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------
-- trend_regression: simple price-vs-time (or log-price-vs-time)
-- regression results, recomputed by the daily batch job
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trend_regression (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    coin_id       INT UNSIGNED NOT NULL,
    run_date      DATE NOT NULL,           -- date the batch job ran
    window_days   INT UNSIGNED NOT NULL,   -- how many days of history used
    use_log_price BOOLEAN NOT NULL DEFAULT FALSE,
    slope         DECIMAL(20,10) NOT NULL,
    intercept     DECIMAL(20,10) NOT NULL,
    r_squared     DECIMAL(6,5),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_trend_regression_coin
        FOREIGN KEY (coin_id) REFERENCES coins(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_coin_run (coin_id, run_date, window_days, use_log_price)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------
-- feature_regression: short-horizon regression using engineered
-- features (rolling volatility, moving averages, volume) instead
-- of raw time
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feature_regression (
    id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    coin_id           INT UNSIGNED NOT NULL,
    run_date          DATE NOT NULL,
    horizon_days      INT UNSIGNED NOT NULL,   -- how far ahead it targets
    model_type        VARCHAR(30) NOT NULL DEFAULT 'linear',
    features_used     JSON NOT NULL,           -- e.g. ["ma_7","ma_30","volatility_14","volume"]
    coefficients      JSON NOT NULL,           -- {"ma_7": 0.42, "volatility_14": -1.1, ...}
    intercept         DECIMAL(20,10) NOT NULL,
    r_squared         DECIMAL(6,5),
    predicted_price   DECIMAL(20,8),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_feature_regression_coin
        FOREIGN KEY (coin_id) REFERENCES coins(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_coin_run_horizon (coin_id, run_date, horizon_days)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------
-- seed the 4 coins we're tracking
-- ---------------------------------------------------------------
INSERT INTO coins (symbol, coingecko_id, name) VALUES
    ('BTC', 'bitcoin', 'Bitcoin'),
    ('ETH', 'ethereum', 'Ethereum'),
    ('SOL', 'solana', 'Solana'),
    ('BNB', 'binancecoin', 'BNB')
ON DUPLICATE KEY UPDATE name = VALUES(name);
