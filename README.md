# Trading Bot — Binance Futures Testnet

A clean, minimal Python CLI application for placing orders on the Binance Futures Testnet (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   ├── logging_config.py  # Structured logging setup
│   └── cli.py             # CLI entry point (argparse)
├── logs/                  # Log files written here at runtime
├── .env.example           # Credentials template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in or register
3. Navigate to **API Management** → generate a new key pair
4. Copy your **API Key** and **Secret Key**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Edit .env and paste your API key and secret
```

`.env` format:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### MARKET Order

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT Order

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

### STOP_LIMIT Order (Bonus)

```bash
python -m bot.cli --symbol ETHUSDT --side SELL --type STOP_LIMIT --quantity 0.1 --price 3400 --stop-price 3450
```

### All Options

```
--symbol       Trading pair (e.g. BTCUSDT)           [required]
--side         BUY or SELL                            [required]
--type         MARKET | LIMIT | STOP_LIMIT            [required]
--quantity     Order quantity                         [required]
--price        Limit price (required for LIMIT/STOP_LIMIT)
--stop-price   Stop trigger price (required for STOP_LIMIT)
--tif          Time in force: GTC | IOC | FOK         [default: GTC]
--log-level    DEBUG | INFO | WARNING | ERROR         [default: INFO]
```

---

## Sample Output

```
==================================================
  ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
==================================================

==================================================
  ORDER RESPONSE
==================================================
  Order ID     : 4751283
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.001
  Executed Qty : 0.001
  Avg Price    : 67320.5
  Price        : 0
  Time in Force: GTC
==================================================

✅  Order placed successfully!
```

---

## Logging

All activity is written to `logs/trading_bot.log` (rotating, max 5 MB).

- **DEBUG**: full request/response payloads
- **INFO**: order lifecycle events
- **ERROR**: API errors, validation failures, network issues

Sample log files from testnet runs are in `logs/`.

---

## Assumptions

- Only USDT-M (linear) futures contracts are supported
- Credentials are loaded from `.env` (never hardcoded)
- `timeInForce` defaults to `GTC` for limit-style orders
- The bot uses `httpx` for HTTP (no `python-binance` dependency)

---

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | HTTP client for REST calls |
| `python-dotenv` | Load `.env` credentials |
