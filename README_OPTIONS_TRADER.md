# ⚡ Options Trader Pro — BankNifty & Nifty50

## 🚀 How to Run

```bash
pip install streamlit yfinance pandas numpy plotly
streamlit run options_trader_pro.py
```

---

## 📦 Features

### 📊 Option Chain Tab
- Full CE/PE chain for **BankNifty** and **Nifty50**
- All strikes around ATM (configurable — 5 to 15 strikes each side)
- **Black-Scholes pricing** with real IV estimated from India VIX
- **Delta, Gamma, Theta, Vega** for every strike
- **Signal column** (STRONG BUY / BUY / NEUTRAL / AVOID) for every CE and PE
- ATM highlighted with gold border
- ITM/OTM classification
- **Staged Profit Booking Levels**: +20%, +40%, +70%, +100% with ₹ values per lot
- **SL at 50%** (configurable in sidebar)
- Deep-dive expander for any strike — full Greeks, profit plan, reasoning

### ⚡ Signal Scanner Tab
- Scans both BankNifty + Nifty50 simultaneously
- Filters: CE Only / PE Only / STRONG BUY Only
- Sorted by signal strength (strongest first)
- Each signal shows: Greeks, profit levels, reasoning, 1-click buy

### 🤖 Auto Trading Tab
- Automated CE/PE entry based on signal strength threshold
- **Market bias filter**: BULLISH market → only CE, BEARISH → only PE
- **Kelly Criterion** position sizing (improves as win rate is tracked)
- **Trailing Stop Loss**: activates after X% profit, moves to breakeven then trails
- **Time-based exit**: exit flat positions after 30 mins
- **VIX guard**: auto trading blocked when VIX > 25
- Live P&L tracking with staged profit booking

### 💼 Portfolio Tab
- All open positions with live Greeks
- Trailing SL status
- Staged profit targets for each position
- Manual square-off per position
- Cumulative P&L chart

### 📜 History Tab
- Full trade history with entry/exit prices
- Win rate, avg win/loss
- CE vs PE P&L breakdown chart
- CSV export

### 📓 Journal & Analytics Tab
- P&L by option type (CE vs PE)
- Win rate by signal strength bucket (50–55%, 55–65%, etc.)
- Dynamic Kelly win rate update

---

## ⚙️ Signal Scoring Logic (per strike)

Each option is scored on:

| Factor | Weight |
|--------|--------|
| Underlying trend (EMA 5/13/21) | ±3 points |
| MACD crossover | ±2 points |
| RSI position | ±2 points |
| 5-day momentum | ±2 points |
| Delta sweet-spot (0.30–0.60) | ±2 points |
| Strike proximity to ATM | ±2 points |
| Gamma level | +1 point |
| Days to expiry | ±2 points |
| VIX level | ±1 point |

**Thresholds:**
- Score ≥ 6 → **STRONG BUY**
- Score ≥ 3 → **BUY**
- Score ≤ -3 → **AVOID**
- Otherwise → **NEUTRAL / HOLD**

---

## 🎯 Profit Booking Strategy

Staged exits reduce risk and lock in gains:

| Level | Action | Default |
|-------|--------|---------|
| L1 | Book partial (20%) profit | +20% from entry |
| L2 | Book more (40%) profit | +40% from entry |
| L3 | Target exit | +70% from entry |
| Full | Complete exit | +100% from entry |
| SL | Stop loss | -50% from entry |
| Trailing | Activates after X% | +50% (configurable) |

---

## 📅 Expiry Management

- Automatically computes next 4 **weekly Thursdays**
- Separate expiry selectors for BankNifty and Nifty50
- Shows days-to-expiry for every strike
- Theta decay warning for < 5 days

---

## ⚠️ Disclaimer

This is a **paper trading simulator** for educational purposes.
- Options involve significant risk — only trade with capital you can afford to lose
- BS pricing is theoretical; real market prices may differ
- Always use a SEBI-registered broker for live trades
- Past signals do not guarantee future performance
