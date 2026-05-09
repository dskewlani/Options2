import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import concurrent.futures
import warnings
import math
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Options Trader Pro — BankNifty & Nifty50",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');

:root {
    --bg:        #06080f;
    --surface:   #0d1117;
    --card:      #111827;
    --border:    #1c2333;
    --accent:    #f0b429;
    --cyan:      #00e5ff;
    --green:     #00e676;
    --red:       #ff1744;
    --purple:    #e040fb;
    --orange:    #ff6d00;
    --text:      #cdd5e0;
    --muted:     #4a5568;
    --ce-color:  #00e5ff;
    --pe-color:  #ff4081;
}

html, body, [class*="css"] {
    font-family: 'Barlow Condensed', sans-serif;
    background: var(--bg);
    color: var(--text);
}

.stApp { background: var(--bg); }

/* Ticker tape */
.ticker-wrap {
    overflow: hidden;
    background: linear-gradient(90deg, #0d1117, #0f1720, #0d1117);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--accent);
    padding: 6px 0;
    margin-bottom: 16px;
    position: relative;
}
.ticker-tape {
    display: flex;
    gap: 40px;
    animation: ticker 40s linear infinite;
    white-space: nowrap;
}
@keyframes ticker {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.ticker-item { font-family: 'Space Mono'; font-size: 0.75rem; color: var(--muted); }
.ticker-item .up   { color: var(--green); }
.ticker-item .down { color: var(--red); }

/* Header */
.main-header {
    font-family: 'Bebas Neue';
    font-size: 3.5rem;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #f0b429, #ff6d00, #ff4081);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 2px;
}
.sub-header {
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* Index cards */
.index-card {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.index-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.index-card.bn::after { background: linear-gradient(90deg, var(--accent), var(--orange)); }
.index-card.nf::after { background: linear-gradient(90deg, var(--cyan), var(--purple)); }
.index-card.vix::after { background: linear-gradient(90deg, var(--red), var(--purple)); }
.index-price {
    font-family: 'Space Mono';
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1;
}
.index-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
}
.up   { color: var(--green) !important; }
.down { color: var(--red) !important; }
.flat { color: var(--accent) !important; }

/* Strike table */
.strike-table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-top: 12px;
}
.strike-header {
    display: grid;
    grid-template-columns: 1fr 80px 80px 80px 120px 80px 80px 80px 1fr;
    padding: 10px 16px;
    background: #0a0e1a;
    border-bottom: 1px solid var(--border);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
}
.ce-header { color: var(--ce-color); }
.pe-header { color: var(--pe-color); }
.atm-row-highlight { background: rgba(240,180,41,0.07) !important; border-left: 3px solid var(--accent) !important; }
.itm-ce { background: rgba(0,229,255,0.04); }
.itm-pe { background: rgba(255,64,129,0.04); }

/* Signal badges */
.sig-buy  { background: rgba(0,230,118,0.12); color: var(--green);  border: 1px solid rgba(0,230,118,0.4); border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; font-family: 'Space Mono'; }
.sig-sell { background: rgba(255,23,68,0.12);  color: var(--red);   border: 1px solid rgba(255,23,68,0.4);  border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; font-family: 'Space Mono'; }
.sig-hold { background: rgba(240,180,41,0.12); color: var(--accent); border: 1px solid rgba(240,180,41,0.4); border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; font-family: 'Space Mono'; }

/* Metric card */
.m-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.m-val  { font-family: 'Space Mono'; font-size: 1.5rem; font-weight: 700; }
.m-lbl  { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px; }

/* CE/PE chips */
.ce-chip { background: rgba(0,229,255,0.1); border: 1px solid rgba(0,229,255,0.3); color: var(--cyan);   border-radius: 6px; padding: 3px 12px; font-size: 0.8rem; font-family: 'Space Mono'; font-weight: 700; }
.pe-chip { background: rgba(255,64,129,0.1); border: 1px solid rgba(255,64,129,0.3); color: #ff4081; border-radius: 6px; padding: 3px 12px; font-size: 0.8rem; font-family: 'Space Mono'; font-weight: 700; }
.atm-chip { background: rgba(240,180,41,0.12); border: 1px solid rgba(240,180,41,0.5); color: var(--accent); border-radius: 6px; padding: 3px 12px; font-size: 0.8rem; font-family: 'Space Mono'; font-weight: 700; }

/* Section title */
.sec-title {
    font-family: 'Bebas Neue';
    font-size: 1.4rem;
    letter-spacing: 3px;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 14px;
}

/* Signal row */
.sig-row {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 14px;
}

/* Trade card */
.trade-card {
    background: linear-gradient(135deg, #0d1117, #111827);
    border-radius: 12px;
    padding: 16px;
    border: 1px solid var(--border);
    margin-bottom: 10px;
}
.trade-card.win-card  { border-left: 3px solid var(--green); }
.trade-card.loss-card { border-left: 3px solid var(--red); }
.trade-card.open-card { border-left: 3px solid var(--cyan); }

/* Greeks */
.greek-box {
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    text-align: center;
}
.greek-val { font-family: 'Space Mono'; font-size: 1rem; font-weight: 700; }
.greek-lbl { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

/* Target/Stop levels */
.level-box {
    border-radius: 8px;
    padding: 8px 14px;
    font-family: 'Space Mono';
    font-size: 0.9rem;
    text-align: center;
    font-weight: 700;
}
.target-box { background: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3); color: var(--green); }
.stop-box   { background: rgba(255,23,68,0.1);  border: 1px solid rgba(255,23,68,0.3);  color: var(--red); }
.entry-box  { background: rgba(0,229,255,0.1);  border: 1px solid rgba(0,229,255,0.3);  color: var(--cyan); }

/* Profit booking levels */
.pb-row {
    background: rgba(0,230,118,0.05);
    border: 1px solid rgba(0,230,118,0.2);
    border-radius: 8px;
    padding: 8px 14px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pb-pct { font-family: 'Space Mono'; font-size: 0.85rem; color: var(--green); font-weight: 700; }
.pb-price { font-family: 'Space Mono'; font-size: 0.9rem; color: var(--text); }
.pb-action { font-size: 0.75rem; color: var(--muted); }

/* Warning / Info boxes */
.warn-box {
    background: rgba(255,109,0,0.08);
    border: 1px solid rgba(255,109,0,0.3);
    border-radius: 10px;
    padding: 12px 16px;
    color: #ffab40;
    font-size: 0.85rem;
    margin-bottom: 10px;
}
.info-box {
    background: rgba(0,229,255,0.06);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    color: #80deea;
    font-size: 0.85rem;
    margin-bottom: 10px;
}
.success-box {
    background: rgba(0,230,118,0.06);
    border: 1px solid rgba(0,230,118,0.25);
    border-radius: 10px;
    padding: 12px 16px;
    color: #69f0ae;
    font-size: 0.85rem;
    margin-bottom: 10px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #f0b429, #ff6d00);
    color: #06080f;
    font-family: 'Bebas Neue';
    font-size: 1rem;
    letter-spacing: 2px;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 400;
}
.stButton > button:hover { opacity: 0.85; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue';
    font-size: 1rem;
    letter-spacing: 2px;
    color: var(--muted);
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "portfolio":        [],
        "history":          [],
        "auto_trading":     False,
        "auto_end":         None,
        "auto_log":         [],
        "auto_pnl":         0.0,
        "capital":          100000.0,
        "_auto_dur":        15,
        "_auto_cap":        5000.0,
        "_auto_max":        5,
        "_auto_str":        60,
        "journal":          [],
        "kelly_wr":         0.55,
        "scan_results":     [],
        "last_chain_bn":    None,
        "last_chain_nf":    None,
        "chain_ts_bn":      None,
        "chain_ts_nf":      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ─── Constants ────────────────────────────────────────────────────────────────
BANKNIFTY_LOT  = 15
NIFTY_LOT      = 25
BANKNIFTY_TICK = 100   # strike interval
NIFTY_TICK     = 50    # strike interval
MIN_VOLUME_OPT = 500   # min OI/volume for options — reasonable liquidity

# ─── Expiry Helpers ───────────────────────────────────────────────────────────
def next_thursday(date=None):
    if date is None:
        date = datetime.now()
    days_ahead = 3 - date.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    return (date + timedelta(days=days_ahead)).date()

def get_expiry_dates(n=4):
    dates = []
    d = datetime.now().date()
    for _ in range(n * 2):
        d = d + timedelta(days=1)
        if d.weekday() == 3:  # Thursday
            dates.append(d)
        if len(dates) == n:
            break
    return dates

def next_monthly_expiry():
    """Last Thursday of current month."""
    now = datetime.now()
    # Find all Thursdays this month
    year, month = now.year, now.month
    last_day = 31
    while True:
        try:
            end = datetime(year, month, last_day)
            break
        except ValueError:
            last_day -= 1
    thursdays = []
    for day in range(1, last_day + 1):
        try:
            d = datetime(year, month, day)
            if d.weekday() == 3:
                thursdays.append(d.date())
        except Exception:
            pass
    if thursdays:
        return thursdays[-1]
    return next_thursday()

# ─── Live Data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=15)
def get_index_data():
    data = {}
    syms = {
        "BANKNIFTY": "^NSEBANK",
        "NIFTY50":   "^NSEI",
        "VIX":       "^INDIAVIX",
        "SENSEX":    "^BSESN",
    }
    for name, sym in syms.items():
        try:
            t    = yf.Ticker(sym)
            df   = t.history(period="2d", interval="1d")
            info = t.fast_info
            lp   = info.last_price if info.last_price else (df["Close"].iloc[-1] if not df.empty else 0)
            prev = float(df["Close"].iloc[-2]) if len(df) >= 2 else float(lp)
            chg  = lp - prev
            pct  = (chg / prev * 100) if prev else 0
            data[name] = {
                "price": float(lp),
                "change": float(chg),
                "pct": float(pct),
                "high": float(df["High"].iloc[-1]) if not df.empty else float(lp),
                "low":  float(df["Low"].iloc[-1])  if not df.empty else float(lp),
                "prev": prev,
            }
        except Exception:
            data[name] = {"price": 0, "change": 0, "pct": 0, "high": 0, "low": 0, "prev": 0}
    return data

@st.cache_data(ttl=30)
def get_ohlc(symbol, period="3mo", interval="1d"):
    try:
        df = yf.Ticker(symbol).history(period=period, interval=interval)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return None

def get_live_price(symbol):
    try:
        t  = yf.Ticker(symbol)
        lp = t.fast_info.last_price
        return float(lp) if lp and np.isfinite(float(lp)) and float(lp) > 0 else None
    except Exception:
        return None

# ─── ATM Strike Calculator ────────────────────────────────────────────────────
def get_atm_strike(spot, tick):
    return round(spot / tick) * tick

def get_strike_range(spot, tick, n_strikes=10):
    atm = get_atm_strike(spot, tick)
    return [atm + (i - n_strikes) * tick for i in range(2 * n_strikes + 1)]

# ─── Black-Scholes (simplified for Greeks) ───────────────────────────────────
def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def black_scholes(S, K, T, r, sigma, option_type="CE"):
    """Returns (price, delta, gamma, theta, vega)"""
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0, 0, 0, 0, 0
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type == "CE":
            price  = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
            delta  = norm_cdf(d1)
        else:
            price  = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
            delta  = norm_cdf(d1) - 1
        gamma = math.exp(-d1**2 / 2) / (S * sigma * math.sqrt(T) * math.sqrt(2 * math.pi))
        theta = (-(S * sigma * math.exp(-d1**2 / 2)) / (2 * math.sqrt(T) * math.sqrt(2 * math.pi))
                 - r * K * math.exp(-r * T) * norm_cdf(d2 if option_type == "CE" else -d2)) / 365
        vega  = S * math.sqrt(T) * math.exp(-d1**2 / 2) / math.sqrt(2 * math.pi) * 0.01
        return round(price, 2), round(delta, 4), round(gamma, 6), round(theta, 2), round(vega, 2)
    except Exception:
        return 0, 0, 0, 0, 0

# ─── Implied Volatility Approximation ────────────────────────────────────────
def estimate_iv(spot, days_to_expiry, vix_level):
    """Estimate IV from VIX + ATM proximity factor."""
    base_iv = vix_level / 100
    time_adj = math.sqrt(max(1, days_to_expiry) / 365)
    return round(base_iv * (1 + 0.1 * time_adj), 4)

# ─── Option Chain Builder ─────────────────────────────────────────────────────
def build_option_chain(index_name, spot, expiry_date, vix_level=15.0, n_strikes=10):
    """
    Build synthetic option chain with BS pricing + signal scoring.
    Uses real underlying data + BS model for realistic pricing.
    """
    tick    = BANKNIFTY_TICK if index_name == "BANKNIFTY" else NIFTY_TICK
    strikes = get_strike_range(spot, tick, n_strikes)
    atm     = get_atm_strike(spot, tick)

    days_to_expiry = max(1, (expiry_date - datetime.now().date()).days)
    T       = days_to_expiry / 365
    r       = 0.065   # risk-free rate (India)
    iv      = estimate_iv(spot, days_to_expiry, vix_level)

    # Get recent OHLC for trend + momentum
    sym_map = {"BANKNIFTY": "^NSEBANK", "NIFTY50": "^NSEI"}
    sym     = sym_map.get(index_name, "^NSEI")
    df      = get_ohlc(sym, period="1mo", interval="1d")

    chain   = []
    for strike in strikes:
        ce_price, ce_delta, ce_gamma, ce_theta, ce_vega = black_scholes(spot, strike, T, r, iv, "CE")
        pe_price, pe_delta, pe_gamma, pe_theta, pe_vega = black_scholes(spot, strike, T, r, iv, "PE")

        # Option type: ITM / ATM / OTM
        if strike < atm:
            ce_type, pe_type = "ITM", "OTM"
        elif strike == atm:
            ce_type = pe_type = "ATM"
        else:
            ce_type, pe_type = "OTM", "ITM"

        # Signal based on Greeks + spot position
        ce_signal = score_option_signal(spot, strike, atm, df, "CE", ce_delta, ce_gamma, days_to_expiry, vix_level)
        pe_signal = score_option_signal(spot, strike, atm, df, "PE", pe_delta, pe_gamma, days_to_expiry, vix_level)

        # Profit targets (scaled to lot size)
        lot     = BANKNIFTY_LOT if index_name == "BANKNIFTY" else NIFTY_LOT
        ce_lots = [
            {"pct": 20,  "price": round(ce_price * 1.20, 2), "label": "Partial (20%)"},
            {"pct": 40,  "price": round(ce_price * 1.40, 2), "label": "Good (40%)"},
            {"pct": 70,  "price": round(ce_price * 1.70, 2), "label": "Target (70%)"},
            {"pct": 100, "price": round(ce_price * 2.00, 2), "label": "Full (100%)"},
        ]
        pe_lots = [
            {"pct": 20,  "price": round(pe_price * 1.20, 2), "label": "Partial (20%)"},
            {"pct": 40,  "price": round(pe_price * 1.40, 2), "label": "Good (40%)"},
            {"pct": 70,  "price": round(pe_price * 1.70, 2), "label": "Target (70%)"},
            {"pct": 100, "price": round(pe_price * 2.00, 2), "label": "Full (100%)"},
        ]

        chain.append({
            "strike":      strike,
            "type":        ce_type,
            "is_atm":      strike == atm,
            # CE
            "ce_price":    ce_price,
            "ce_delta":    ce_delta,
            "ce_gamma":    ce_gamma,
            "ce_theta":    ce_theta,
            "ce_vega":     ce_vega,
            "ce_signal":   ce_signal,
            "ce_sl":       round(ce_price * 0.50, 2),  # 50% SL
            "ce_targets":  ce_lots,
            # PE
            "pe_price":    pe_price,
            "pe_delta":    pe_delta,
            "pe_gamma":    pe_gamma,
            "pe_theta":    pe_theta,
            "pe_vega":     pe_vega,
            "pe_signal":   pe_signal,
            "pe_sl":       round(pe_price * 0.50, 2),
            "pe_targets":  pe_lots,
            # Meta
            "lot":         lot,
            "iv":          round(iv * 100, 1),
            "days_exp":    days_to_expiry,
        })
    return chain

def score_option_signal(spot, strike, atm, df, opt_type, delta, gamma, days_to_exp, vix):
    """
    Score option signal: BUY / SELL / HOLD with reasoning.
    Combines trend, momentum, Greeks, IV, and time decay considerations.
    """
    score = 0
    reasons = []

    # ── Trend from underlying ─────────────────────────────────────────────────
    if df is not None and len(df) >= 10:
        close  = df["Close"].astype(float)
        ema5   = close.ewm(span=5,  adjust=False).mean()
        ema13  = close.ewm(span=13, adjust=False).mean()
        ema21  = close.ewm(span=21, adjust=False).mean()
        rsi14  = _compute_rsi(close, 14)

        trend_up = float(close.iloc[-1]) > float(ema13.iloc[-1]) > float(ema21.iloc[-1])
        trend_dn = float(close.iloc[-1]) < float(ema13.iloc[-1]) < float(ema21.iloc[-1])
        rsi      = float(rsi14.iloc[-1]) if not rsi14.empty else 50

        # Momentum (last 5 days)
        mom5 = float((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100) if len(close) >= 5 else 0

        if opt_type == "CE":
            if trend_up:
                score += 3; reasons.append("Underlying uptrend (EMA stack bullish) → +3")
            elif trend_dn:
                score -= 2; reasons.append("Underlying downtrend → -2 (unfavourable for CE)")
            if rsi < 45:
                score += 1; reasons.append(f"RSI {rsi:.0f} oversold — bounce likely → +1")
            elif rsi > 70:
                score -= 1; reasons.append(f"RSI {rsi:.0f} overbought — CE risky → -1")
            if mom5 > 1.5:
                score += 2; reasons.append(f"5D momentum +{mom5:.1f}% → +2")
            elif mom5 < -1.5:
                score -= 1; reasons.append(f"5D momentum {mom5:.1f}% → -1")
        else:  # PE
            if trend_dn:
                score += 3; reasons.append("Underlying downtrend (EMA stack bearish) → +3")
            elif trend_up:
                score -= 2; reasons.append("Underlying uptrend → -2 (unfavourable for PE)")
            if rsi > 55:
                score += 1; reasons.append(f"RSI {rsi:.0f} — elevated, put favourable → +1")
            elif rsi < 30:
                score -= 1; reasons.append(f"RSI {rsi:.0f} oversold — PE risky → -1")
            if mom5 < -1.5:
                score += 2; reasons.append(f"5D momentum {mom5:.1f}% → +2")
            elif mom5 > 1.5:
                score -= 1; reasons.append(f"5D momentum +{mom5:.1f}% → -1")

    # ── Greeks Assessment ─────────────────────────────────────────────────────
    # Prefer 0.3-0.6 delta (sweet spot — not too far OTM, not pure intrinsic)
    abs_delta = abs(delta)
    if 0.3 <= abs_delta <= 0.6:
        score += 2; reasons.append(f"|Delta|={abs_delta:.2f} optimal sweet-spot → +2")
    elif 0.15 <= abs_delta < 0.3:
        score += 1; reasons.append(f"|Delta|={abs_delta:.2f} slightly OTM but tradeable → +1")
    elif abs_delta < 0.15:
        score -= 2; reasons.append(f"|Delta|={abs_delta:.2f} too far OTM — low probability → -2")
    elif abs_delta > 0.7:
        score += 1; reasons.append(f"|Delta|={abs_delta:.2f} deep ITM — high delta → +1")

    # Gamma: high gamma = high leverage (good near ATM near expiry)
    if gamma > 0.0005:
        score += 1; reasons.append(f"Gamma={gamma:.5f} high — good near ATM → +1")

    # ── Time Decay (Theta) ────────────────────────────────────────────────────
    if days_to_exp <= 2:
        score -= 2; reasons.append("⚠️ Only 1-2 days to expiry — theta burn very high → -2")
    elif days_to_exp <= 5:
        score -= 1; reasons.append(f"{days_to_exp}d to expiry — elevated theta decay → -1")
    else:
        score += 1; reasons.append(f"{days_to_exp}d to expiry — decent time value → +1")

    # ── VIX / IV ──────────────────────────────────────────────────────────────
    if vix > 20:
        score += 1; reasons.append(f"VIX={vix:.1f} elevated → options overpriced, premium selling favoured (but use for momentum plays) → +1")
    elif vix < 13:
        score += 1; reasons.append(f"VIX={vix:.1f} low → buy options for breakout moves → +1")

    # ── Strike Position ───────────────────────────────────────────────────────
    pct_from_atm = (strike - spot) / spot * 100
    if opt_type == "CE":
        if 0 <= pct_from_atm <= 0.5:
            score += 2; reasons.append("Near-ATM CE — best liquidity → +2")
        elif 0.5 < pct_from_atm <= 1.5:
            score += 1; reasons.append("Slightly OTM CE — good R/R → +1")
        elif pct_from_atm > 3:
            score -= 2; reasons.append("Very far OTM CE — lottery ticket → -2")
        elif pct_from_atm < -2:
            score += 0; reasons.append("Deep ITM CE — low leverage")
    else:  # PE
        pct_itm = (spot - strike) / spot * 100
        if 0 <= pct_itm <= 0.5:
            score += 2; reasons.append("Near-ATM PE — best liquidity → +2")
        elif 0.5 < pct_itm <= 1.5:
            score += 1; reasons.append("Slightly OTM PE — good R/R → +1")
        elif pct_itm > 3:
            score -= 2; reasons.append("Very far OTM PE — lottery ticket → -2")

    # ── Final classification ──────────────────────────────────────────────────
    if score >= 6:
        signal = "STRONG BUY"
        strength = min(95, 60 + score * 3)
    elif score >= 3:
        signal = "BUY"
        strength = min(80, 50 + score * 4)
    elif score <= -3:
        signal = "AVOID"
        strength = max(10, 50 + score * 4)
    elif score <= -1:
        signal = "HOLD"
        strength = 45
    else:
        signal = "NEUTRAL"
        strength = 50

    return {
        "signal":   signal,
        "score":    score,
        "strength": strength,
        "reasons":  reasons,
    }

def _compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).ewm(span=period, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=period, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

# ─── Compute Indicators for underlying ───────────────────────────────────────
def compute_index_indicators(df):
    if df is None or len(df) < 14:
        return {}
    try:
        c = df["Close"].astype(float)
        h = df["High"].astype(float)
        l = df["Low"].astype(float)
        v = df["Volume"].astype(float) if "Volume" in df.columns else pd.Series([1]*len(c), index=c.index)

        rsi14   = _compute_rsi(c, 14)
        ema5    = c.ewm(span=5,  adjust=False).mean()
        ema13   = c.ewm(span=13, adjust=False).mean()
        ema21   = c.ewm(span=21, adjust=False).mean()
        ema50   = c.ewm(span=50, adjust=False).mean()
        ema12   = c.ewm(span=12, adjust=False).mean()
        ema26   = c.ewm(span=26, adjust=False).mean()
        macd    = ema12 - ema26
        signal  = macd.ewm(span=9, adjust=False).mean()
        hist    = macd - signal
        sma20   = c.rolling(20).mean()
        std20   = c.rolling(20).std()
        bb_u    = sma20 + 2 * std20
        bb_l    = sma20 - 2 * std20
        bb_rng  = (bb_u - bb_l).replace(0, np.nan)
        bb_pct  = (c - bb_l) / bb_rng
        # ATR
        tr      = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atr     = tr.rolling(14).mean()
        # Stoch
        low14   = l.rolling(14).min()
        high14  = h.rolling(14).max()
        sk      = 100 * (c - low14) / (high14 - low14 + 0.001)
        sd      = sk.rolling(3).mean()
        # ADX
        pdm = (h.diff()).clip(lower=0)
        ndm = (-l.diff()).clip(lower=0)
        atr_s   = atr.replace(0, np.nan)
        pdi     = 100 * pdm.ewm(span=14).mean() / atr_s
        ndi     = 100 * ndm.ewm(span=14).mean() / atr_s
        dx      = 100 * (pdi - ndi).abs() / (pdi + ndi + 0.001)
        adx     = dx.ewm(span=14).mean()
        # S/R
        pivot   = (h.iloc[-1] + l.iloc[-1] + c.iloc[-1]) / 3
        support1 = 2 * pivot - h.iloc[-1]
        resist1  = 2 * pivot - l.iloc[-1]
        # Momentum
        mom5    = float((c.iloc[-1] - c.iloc[-5]) / c.iloc[-5] * 100) if len(c) >= 5 else 0
        mom20   = float((c.iloc[-1] - c.iloc[-20]) / c.iloc[-20] * 100) if len(c) >= 20 else 0

        return {
            "rsi":       float(rsi14.iloc[-1]),
            "macd":      float(macd.iloc[-1]),
            "macd_sig":  float(signal.iloc[-1]),
            "macd_hist": float(hist.iloc[-1]),
            "ema5":      float(ema5.iloc[-1]),
            "ema13":     float(ema13.iloc[-1]),
            "ema21":     float(ema21.iloc[-1]),
            "ema50":     float(ema50.iloc[-1]),
            "bb_pct":    float(bb_pct.iloc[-1]),
            "bb_u":      float(bb_u.iloc[-1]),
            "bb_l":      float(bb_l.iloc[-1]),
            "atr":       float(atr.iloc[-1]),
            "stoch_k":   float(sk.iloc[-1]),
            "stoch_d":   float(sd.iloc[-1]),
            "adx":       float(adx.iloc[-1]),
            "pdi":       float(pdi.iloc[-1]),
            "ndi":       float(ndi.iloc[-1]),
            "close":     float(c.iloc[-1]),
            "pivot":     float(pivot),
            "support1":  float(support1),
            "resist1":   float(resist1),
            "mom5":      mom5,
            "mom20":     mom20,
            "vol_ratio": float(v.iloc[-1] / v.rolling(20).mean().iloc[-1]) if len(v) >= 20 else 1.0,
        }
    except Exception:
        return {}

# ─── Overall Index Signal ─────────────────────────────────────────────────────
def get_index_signal(indicators):
    """Returns BULLISH / BEARISH / SIDEWAYS + score for the underlying."""
    if not indicators:
        return "SIDEWAYS", 50, []
    buy = 0; sell = 0; reasons = []
    rsi       = indicators.get("rsi", 50)
    macd      = indicators.get("macd", 0)
    msig      = indicators.get("macd_sig", 0)
    bb_pct    = indicators.get("bb_pct", 0.5)
    sk        = indicators.get("stoch_k", 50)
    sd        = indicators.get("stoch_d", 50)
    adx       = indicators.get("adx", 20)
    pdi       = indicators.get("pdi", 25)
    ndi       = indicators.get("ndi", 25)
    close     = indicators.get("close", 0)
    ema13     = indicators.get("ema13", 0)
    ema21     = indicators.get("ema21", 0)
    ema50     = indicators.get("ema50", 0)
    mom5      = indicators.get("mom5", 0)

    if rsi < 35:   buy += 2;  reasons.append(f"RSI {rsi:.0f} — oversold → BUY +2")
    elif rsi < 45: buy += 1;  reasons.append(f"RSI {rsi:.0f} — mildly weak → BUY +1")
    elif rsi > 70: sell += 2; reasons.append(f"RSI {rsi:.0f} — overbought → SELL +2")
    elif rsi > 60: sell += 1; reasons.append(f"RSI {rsi:.0f} — elevated → SELL +1")

    if macd > msig:  buy += 2;  reasons.append("MACD bullish crossover → BUY +2")
    else:            sell += 2; reasons.append("MACD bearish crossover → SELL +2")

    if bb_pct < 0.15:  buy += 2;  reasons.append(f"BB% {bb_pct:.2f} — near lower band → BUY +2")
    elif bb_pct > 0.85: sell += 2; reasons.append(f"BB% {bb_pct:.2f} — near upper band → SELL +2")

    if sk < 25 and sk > sd:  buy += 2;  reasons.append(f"Stoch K={sk:.0f} oversold crossing up → BUY +2")
    elif sk > 75 and sk < sd: sell += 2; reasons.append(f"Stoch K={sk:.0f} overbought crossing dn → SELL +2")

    if close > ema13 > ema21: buy += 2;  reasons.append("Price > EMA13 > EMA21 bullish stack → BUY +2")
    elif close < ema13 < ema21: sell += 2; reasons.append("Price < EMA13 < EMA21 bearish stack → SELL +2")

    if adx > 25:
        if pdi > ndi: buy += 2;  reasons.append(f"ADX={adx:.0f} strong uptrend → BUY +2")
        else:         sell += 2; reasons.append(f"ADX={adx:.0f} strong downtrend → SELL +2")

    if mom5 > 1.5:  buy += 1;  reasons.append(f"5D momentum +{mom5:.1f}% → BUY +1")
    elif mom5 < -1.5: sell += 1; reasons.append(f"5D momentum {mom5:.1f}% → SELL +1")

    total = max(buy + sell, 1)
    if buy > sell:
        sig      = "BULLISH"
        strength = min(95, int(buy / total * 100))
    elif sell > buy:
        sig      = "BEARISH"
        strength = min(95, int(sell / total * 100))
    else:
        sig      = "SIDEWAYS"
        strength = 50

    return sig, strength, reasons

# ─── Trade Cost (F&O) ─────────────────────────────────────────────────────────
def fno_trade_cost(premium, lots, lot_size, trade_type="BUY"):
    turnover   = premium * lots * lot_size
    brokerage  = min(40.0, turnover * 0.0003)
    stt        = turnover * 0.0005 if trade_type == "SELL" else 0  # STT only on sell side in options
    exchange   = turnover * 0.0000495
    sebi       = turnover * 0.000001
    gst        = (brokerage + exchange + sebi) * 0.18
    stamp      = turnover * 0.00003 if trade_type == "BUY" else 0
    return round(brokerage + stt + exchange + sebi + gst + stamp, 2)

# ─── Kelly Sizing for Options ─────────────────────────────────────────────────
def kelly_lots(capital, win_rate, rr, strength, lot_value):
    try:
        if rr <= 0: return 1
        f = win_rate - (1 - win_rate) / rr
        f = max(0.03, min(0.20, f))
        s_mult = 0.5 + (strength / 100) * 0.5
        allocated = capital * f * s_mult
        lots = max(1, int(allocated / lot_value))
        return min(lots, 5)  # cap at 5 lots
    except Exception:
        return 1

# ─── Build Scannable Option Signals ──────────────────────────────────────────
def scan_option_signals(index_name, spot, vix, expiry_date, n_strikes=8):
    chain = build_option_chain(index_name, spot, expiry_date, vix, n_strikes)
    signals = []
    for row in chain:
        for otype in ["CE", "PE"]:
            sig_key  = f"{otype.lower()}_signal"
            pr_key   = f"{otype.lower()}_price"
            sig_data = row[sig_key]
            if sig_data["signal"] in ("BUY", "STRONG BUY") and row[pr_key] > 0:
                signals.append({
                    "index":    index_name,
                    "expiry":   expiry_date,
                    "strike":   row["strike"],
                    "type":     otype,
                    "symbol":   f"{index_name}{expiry_date.strftime('%d%b%y').upper()}{row['strike']}{otype}",
                    "price":    row[pr_key],
                    "sl":       row[f"{otype.lower()}_sl"],
                    "targets":  row[f"{otype.lower()}_targets"],
                    "signal":   sig_data["signal"],
                    "strength": sig_data["strength"],
                    "score":    sig_data["score"],
                    "delta":    row[f"{otype.lower()}_delta"],
                    "gamma":    row[f"{otype.lower()}_gamma"],
                    "theta":    row[f"{otype.lower()}_theta"],
                    "vega":     row[f"{otype.lower()}_vega"],
                    "iv":       row["iv"],
                    "lot":      row["lot"],
                    "days_exp": row["days_exp"],
                    "reasons":  sig_data["reasons"],
                    "is_atm":   row["is_atm"],
                    "opt_type": row["type"],   # ITM/ATM/OTM
                })
    signals.sort(key=lambda x: -x["strength"])
    return signals

# ──────────────────────────────────────────────────────────────────────────────
# UI — Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">OPTIONS TRADER PRO</div>
<div class="sub-header">BankNifty & Nifty50 · Live CE/PE Chains · BS Pricing · Greeks · Smart Profit Booking</div>
""", unsafe_allow_html=True)

# ─── Live Index Data ──────────────────────────────────────────────────────────
idx = get_index_data()
bn  = idx.get("BANKNIFTY", {})
nf  = idx.get("NIFTY50",   {})
vx  = idx.get("VIX",       {})
sx  = idx.get("SENSEX",    {})

bn_spot  = bn.get("price", 50000)
nf_spot  = nf.get("price", 22000)
vix_val  = vx.get("price", 15.0)

# ── Ticker Tape ───────────────────────────────────────────────────────────────
def fmt_ticker(name, price, pct):
    cls = "up" if pct >= 0 else "down"
    arrow = "▲" if pct >= 0 else "▼"
    return f'<span class="ticker-item">{name}: <span class="{cls}">{price:,.2f} {arrow}{abs(pct):.2f}%</span></span>'

tape_html = " · ".join([
    fmt_ticker("BANKNIFTY", bn_spot, bn.get("pct", 0)),
    fmt_ticker("NIFTY50",   nf_spot, nf.get("pct", 0)),
    fmt_ticker("VIX",       vix_val, vx.get("pct", 0)),
    fmt_ticker("SENSEX",    sx.get("price", 72000), sx.get("pct", 0)),
    fmt_ticker("BANKNIFTY", bn_spot, bn.get("pct", 0)),
    fmt_ticker("NIFTY50",   nf_spot, nf.get("pct", 0)),
    fmt_ticker("VIX",       vix_val, vx.get("pct", 0)),
    fmt_ticker("SENSEX",    sx.get("price", 72000), sx.get("pct", 0)),
])
st.markdown(f'<div class="ticker-wrap"><div class="ticker-tape">{tape_html}</div></div>', unsafe_allow_html=True)

# ── Index Cards ───────────────────────────────────────────────────────────────
ic1, ic2, ic3, ic4 = st.columns(4)

def idx_card(label, price, chg, pct, css_class):
    color = "up" if pct >= 0 else "down"
    arrow = "▲" if pct >= 0 else "▼"
    return f"""<div class="index-card {css_class}">
        <div class="index-label">{label}</div>
        <div class="index-price {color}">{price:,.2f}</div>
        <div style="font-family:'Space Mono';font-size:0.8rem;margin-top:4px;" class="{color}">
            {arrow} {chg:+,.2f} ({pct:+.2f}%)
        </div>
    </div>"""

with ic1: st.markdown(idx_card("BANKNIFTY", bn_spot, bn.get("change",0), bn.get("pct",0), "bn"), unsafe_allow_html=True)
with ic2: st.markdown(idx_card("NIFTY 50",  nf_spot, nf.get("change",0), nf.get("pct",0), "nf"), unsafe_allow_html=True)
with ic3:
    vix_color = "down" if vix_val > 20 else ("up" if vix_val < 13 else "flat")
    st.markdown(f"""<div class="index-card vix">
        <div class="index-label">INDIA VIX</div>
        <div class="index-price {vix_color}">{vix_val:.2f}</div>
        <div style="font-family:'Space Mono';font-size:0.75rem;margin-top:4px;color:var(--muted);">
            {"🔴 HIGH RISK" if vix_val>20 else ("🟢 CALM" if vix_val<13 else "🟡 MODERATE")}
        </div></div>""", unsafe_allow_html=True)
with ic4:
    bn_atm = get_atm_strike(bn_spot, BANKNIFTY_TICK)
    nf_atm = get_atm_strike(nf_spot, NIFTY_TICK)
    st.markdown(f"""<div class="index-card" style="border-top-color:var(--green)">
        <div class="index-label">ATM STRIKES</div>
        <div style="font-family:'Space Mono';font-size:1rem;font-weight:700;margin-top:4px;">
            <span style="color:var(--accent)">BN</span> {bn_atm:,}
        </div>
        <div style="font-family:'Space Mono';font-size:1rem;font-weight:700;">
            <span style="color:var(--cyan)">NF</span> {nf_atm:,}
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if vix_val > 20:
    st.markdown(f'<div class="warn-box">⚠️ <b>HIGH VIX ALERT — {vix_val:.1f}</b>: Options are expensive. Prefer selling premium or use spreads. Wide stops recommended.</div>', unsafe_allow_html=True)
if vix_val < 13:
    st.markdown(f'<div class="info-box">📊 <b>LOW VIX — {vix_val:.1f}</b>: Options cheap — good time to BUY directional calls/puts. Look for breakouts.</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    capital = st.number_input("💰 Total Capital (₹)", value=100000, step=10000)
    st.session_state.capital = float(capital)
    base_lot_cap = st.number_input("Capital per Trade (₹)", value=10000, step=2500)
    use_kelly  = st.checkbox("🧮 Kelly Criterion Sizing", value=True)
    use_trail  = st.checkbox("🎯 Trailing Profit Booking", value=True)
    use_time_x = st.checkbox("⏱️ Time Exit (30 min)", value=True)

    st.markdown("---")
    st.markdown("### 📅 Expiry Selection")
    expiries = get_expiry_dates(4)
    exp_labels = [f"{e.strftime('%d %b %Y')} (Thu)" for e in expiries]
    exp_sel_bn = st.selectbox("BankNifty Expiry", exp_labels, key="exp_bn")
    exp_sel_nf = st.selectbox("Nifty50 Expiry",   exp_labels, key="exp_nf")
    exp_bn = expiries[exp_labels.index(exp_sel_bn)]
    exp_nf = expiries[exp_labels.index(exp_sel_nf)]

    st.markdown("---")
    st.markdown("### 🎯 Strike Range")
    n_strikes = st.slider("Strikes either side of ATM", 5, 15, 8, 1)
    min_sig_str = st.slider("Min Signal Strength (%)", 40, 90, 55, 5)

    st.markdown("---")
    st.markdown("### 📊 Profit Booking Levels")
    pb1 = st.slider("Level 1 — Book X% profit at", 10, 40,  20, 5)
    pb2 = st.slider("Level 2 — Book X% profit at", 25, 60,  40, 5)
    pb3 = st.slider("Level 3 — Book X% profit at", 50, 100, 70, 5)
    pb4 = st.slider("Trail SL after profit of",     30, 80,  50, 5)

    st.markdown("---")
    st.markdown("### 📈 Session Stats")
    hist_pnl = sum(t.get("pnl", 0) for t in st.session_state.history)
    open_pnl = sum(t.get("pnl", 0) for t in st.session_state.portfolio)
    kelly_wr = st.session_state.get("kelly_wr", 0.55)
    st.metric("Open Positions", len(st.session_state.portfolio))
    st.metric("Closed Trades",  len(st.session_state.history))
    st.metric("Unrealised P&L", f"₹{open_pnl:,.0f}")
    st.metric("Realized P&L",   f"₹{hist_pnl:,.0f}")
    st.markdown(f'<div class="info-box" style="font-size:0.78rem;">🧮 Kelly Win Rate: <b>{kelly_wr*100:.1f}%</b><br>({len(st.session_state.journal)} trades)</div>', unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Option Chain", "⚡ Signal Scanner", "🤖 Auto Trading",
    "💼 Portfolio", "📜 History", "📓 Journal"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Option Chain
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="sec-title">📊 LIVE OPTION CHAIN — CE/PE WITH SIGNALS</div>', unsafe_allow_html=True)

    chain_idx = st.radio("Select Index", ["BANKNIFTY", "NIFTY50"], horizontal=True, key="chain_idx_sel")
    spot_val  = bn_spot if chain_idx == "BANKNIFTY" else nf_spot
    exp_date  = exp_bn  if chain_idx == "BANKNIFTY" else exp_nf
    tick      = BANKNIFTY_TICK if chain_idx == "BANKNIFTY" else NIFTY_TICK
    lot_size  = BANKNIFTY_LOT  if chain_idx == "BANKNIFTY" else NIFTY_LOT
    atm       = get_atm_strike(spot_val, tick)

    st.markdown(f"""
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:12px;flex-wrap:wrap;">
        <div class="atm-chip">ATM: {atm:,}</div>
        <div class="ce-chip">LOT SIZE: {lot_size}</div>
        <div class="pe-chip">EXPIRY: {exp_date.strftime('%d %b %Y')}</div>
        <div style="font-family:'Space Mono';font-size:0.78rem;color:var(--muted);">
            Spot: ₹{spot_val:,.2f} | Days to Expiry: {(exp_date - datetime.now().date()).days}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Underlying indicators
    sym_map2 = {"BANKNIFTY": "^NSEBANK", "NIFTY50": "^NSEI"}
    df_und  = get_ohlc(sym_map2[chain_idx], period="3mo", interval="1d")
    ind_und = compute_index_indicators(df_und)
    idx_sig, idx_str, idx_reasons = get_index_signal(ind_und)

    # Index signal banner
    sig_color = "var(--green)" if idx_sig == "BULLISH" else ("var(--red)" if idx_sig == "BEARISH" else "var(--accent)")
    sig_icon  = "🐂" if idx_sig == "BULLISH" else ("🐻" if idx_sig == "BEARISH" else "↔️")
    st.markdown(f"""
    <div style="background:rgba(0,0,0,0.3);border:1px solid {sig_color};border-radius:12px;
         padding:14px 20px;margin-bottom:14px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div>
            <div style="font-family:'Bebas Neue';font-size:1.4rem;color:{sig_color};letter-spacing:2px;">
                {sig_icon} {chain_idx} IS {idx_sig}
            </div>
            <div style="font-size:0.8rem;color:var(--muted);">Signal Strength: {idx_str}% | 
                {'✅ Prefer CE (BUY CALLS)' if idx_sig=='BULLISH' else ('✅ Prefer PE (BUY PUTS)' if idx_sig=='BEARISH' else '⚠️ Sideways — Use Straddle/Strangle')}
            </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
    """ + "".join([
        f'<div style="font-size:0.72rem;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:6px;padding:4px 10px;color:var(--muted);">{r[:60]}</div>'
        for r in idx_reasons[:4]
    ]) + "</div></div>", unsafe_allow_html=True)

    # Indicators row
    if ind_und:
        ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
        ic1.metric("RSI 14",   f"{ind_und.get('rsi',0):.1f}")
        ic2.metric("MACD",     f"{ind_und.get('macd',0):.2f}")
        ic3.metric("ADX",      f"{ind_und.get('adx',0):.1f}")
        ic4.metric("BB %",     f"{ind_und.get('bb_pct',0):.2f}")
        ic5.metric("5D Mom",   f"{ind_und.get('mom5',0):+.2f}%")
        ic6.metric("Stoch K",  f"{ind_und.get('stoch_k',0):.1f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Build chain
    if st.button(f"🔄 Load {chain_idx} Option Chain", use_container_width=False):
        with st.spinner("Building option chain…"):
            chain = build_option_chain(chain_idx, spot_val, exp_date, vix_val, n_strikes)
        if chain_idx == "BANKNIFTY":
            st.session_state.last_chain_bn  = chain
            st.session_state.chain_ts_bn    = datetime.now()
        else:
            st.session_state.last_chain_nf  = chain
            st.session_state.chain_ts_nf    = datetime.now()

    chain_key = f"last_chain_{'bn' if chain_idx=='BANKNIFTY' else 'nf'}"
    ts_key    = f"chain_ts_{'bn' if chain_idx=='BANKNIFTY' else 'nf'}"
    chain     = st.session_state.get(chain_key)
    chain_ts  = st.session_state.get(ts_key)

    if chain:
        if chain_ts:
            st.markdown(f'<div class="info-box" style="padding:6px 12px;font-size:0.78rem;">Last updated: {chain_ts.strftime("%H:%M:%S")} · {len(chain)} strikes loaded · Powered by Black-Scholes</div>', unsafe_allow_html=True)

        # ── Chain Table Headers ───────────────────────────────────────────────
        st.markdown("""
        <div style="display:grid;grid-template-columns:1.2fr 0.8fr 0.8fr 0.6fr 1fr 1fr 0.6fr 0.8fr 0.8fr 1.2fr;
             padding:10px 16px;background:#080c14;border:1px solid var(--border);border-radius:10px 10px 0 0;
             font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;gap:4px;">
            <div style="color:var(--ce-color);text-align:left;">CE Signal</div>
            <div style="color:var(--ce-color);text-align:center;">CE Price</div>
            <div style="color:var(--ce-color);text-align:center;">CE Delta</div>
            <div style="color:var(--ce-color);text-align:center;">CE IV%</div>
            <div style="color:var(--ce-color);text-align:center;">CE Targets</div>
            <div style="text-align:center;font-size:1rem;font-family:'Bebas Neue';color:var(--accent);letter-spacing:2px;">STRIKE</div>
            <div style="color:var(--pe-color);text-align:center;">PE IV%</div>
            <div style="color:var(--pe-color);text-align:center;">PE Delta</div>
            <div style="color:var(--pe-color);text-align:center;">PE Price</div>
            <div style="color:var(--pe-color);text-align:right;">PE Signal</div>
        </div>""", unsafe_allow_html=True)

        for row in chain:
            is_atm    = row["is_atm"]
            ce_sig    = row["ce_signal"]
            pe_sig    = row["pe_signal"]
            bg_style  = "background:rgba(240,180,41,0.07);border-left:3px solid var(--accent);border-right:3px solid var(--accent);" if is_atm else ""
            atm_label = " 🎯ATM" if is_atm else ""

            def sig_badge(sig_data):
                s = sig_data["signal"]
                if "BUY" in s:   return f'<span class="sig-buy">{s}</span>'
                elif s == "AVOID": return f'<span class="sig-sell">AVOID</span>'
                else:              return f'<span class="sig-hold">{s}</span>'

            ce_t1 = row["ce_targets"][1]["price"]  # 40% target
            pe_t1 = row["pe_targets"][1]["price"]

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1.2fr 0.8fr 0.8fr 0.6fr 1fr 1fr 0.6fr 0.8fr 0.8fr 1.2fr;
                 padding:10px 16px;border:1px solid var(--border);border-top:none;{bg_style}
                 gap:4px;align-items:center;font-size:0.82rem;">
                <div>{sig_badge(ce_sig)}</div>
                <div style="text-align:center;font-family:'Space Mono';color:var(--ce-color);font-weight:700;">₹{row['ce_price']:.2f}</div>
                <div style="text-align:center;font-family:'Space Mono';font-size:0.75rem;">{row['ce_delta']:.3f}</div>
                <div style="text-align:center;font-size:0.75rem;color:var(--muted);">{row['iv']}%</div>
                <div style="text-align:center;font-size:0.73rem;color:var(--green);">T1:₹{ce_t1} / SL:₹{row['ce_sl']}</div>
                <div style="text-align:center;font-family:'Bebas Neue';font-size:1.2rem;color:var(--accent);letter-spacing:1px;">
                    {row['strike']:,}{atm_label}
                </div>
                <div style="text-align:center;font-size:0.75rem;color:var(--muted);">{row['iv']}%</div>
                <div style="text-align:center;font-family:'Space Mono';font-size:0.75rem;">{row['pe_delta']:.3f}</div>
                <div style="text-align:center;font-family:'Space Mono';color:#ff4081;font-weight:700;">₹{row['pe_price']:.2f}</div>
                <div style="text-align:right;">{sig_badge(pe_sig)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="border:1px solid var(--border);border-top:none;border-radius:0 0 10px 10px;padding:8px 16px;background:#080c14;font-size:0.7rem;color:var(--muted);">Prices via Black-Scholes · Delta/Gamma/Theta/Vega calculated · IV derived from India VIX · Click any strike below for deep analysis</div>', unsafe_allow_html=True)

        # ── Deep Dive on selected strike ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 STRIKE DEEP DIVE</div>', unsafe_allow_html=True)
        strike_options = [f"{r['strike']:,} {'🎯ATM' if r['is_atm'] else r['type']}" for r in chain]
        sel_strike_lbl = st.selectbox("Select Strike for Deep Analysis", strike_options, key="deep_strike")
        sel_idx_val    = [i for i, l in enumerate(strike_options) if l == sel_strike_lbl][0]
        sel_row        = chain[sel_idx_val]

        da1, da2 = st.columns(2)
        for col, otype, color in [(da1, "CE", "var(--ce-color)"), (da2, "PE", "#ff4081")]:
            with col:
                pr    = sel_row[f"{otype.lower()}_price"]
                sig_d = sel_row[f"{otype.lower()}_signal"]
                sl    = sel_row[f"{otype.lower()}_sl"]
                tgts  = sel_row[f"{otype.lower()}_targets"]
                dlt   = sel_row[f"{otype.lower()}_delta"]
                gam   = sel_row[f"{otype.lower()}_gamma"]
                tht   = sel_row[f"{otype.lower()}_theta"]
                veg   = sel_row[f"{otype.lower()}_vega"]
                lot   = sel_row["lot"]

                st.markdown(f"""
                <div style="background:var(--card);border:1px solid {color};border-radius:12px;padding:16px;">
                    <div style="font-family:'Bebas Neue';font-size:1.6rem;color:{color};letter-spacing:2px;">
                        {sel_row['strike']:,} {otype} · ₹{pr:.2f}
                    </div>
                    <div style="font-size:0.8rem;color:var(--muted);margin-bottom:12px;">
                        {sel_row['type']} · Lot: {lot} · Days: {sel_row['days_exp']} · IV: {sel_row['iv']}%
                    </div>
                """, unsafe_allow_html=True)

                # Greeks row
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:12px;">
                    <div class="greek-box"><div class="greek-val" style="color:{color}">{dlt:.4f}</div><div class="greek-lbl">DELTA</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--purple)">{gam:.5f}</div><div class="greek-lbl">GAMMA</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--red)">{tht:.2f}</div><div class="greek-lbl">THETA</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--green)">{veg:.2f}</div><div class="greek-lbl">VEGA</div></div>
                </div>
                """, unsafe_allow_html=True)

                # Entry / SL
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
                    <div class="level-box entry-box">ENTRY<br>₹{pr:.2f}</div>
                    <div class="level-box stop-box">SL (50%)<br>₹{sl:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                # Profit targets
                st.markdown("<b style='font-size:0.8rem;color:var(--muted);'>PROFIT BOOKING LEVELS</b>", unsafe_allow_html=True)
                for t in tgts:
                    profit_pts = t["price"] - pr
                    profit_lot = profit_pts * lot
                    st.markdown(f"""
                    <div class="pb-row">
                        <span class="pb-pct">+{t['pct']}%</span>
                        <span class="pb-price">₹{t['price']:.2f}</span>
                        <span class="pb-action">{t['label']}</span>
                        <span style="font-family:'Space Mono';font-size:0.8rem;color:var(--green);">+₹{profit_lot:.0f}/lot</span>
                    </div>""", unsafe_allow_html=True)

                # Signal reasons
                st.markdown(f"<br><b style='font-size:0.8rem;color:var(--muted);'>SIGNAL REASONING ({sig_d['signal']} · {sig_d['strength']}%)</b>", unsafe_allow_html=True)
                for r in sig_d["reasons"][:6]:
                    ico = "✅" if "+" in r and "-" not in r else ("⚠️" if "⚠" in r else ("🔻" if "-" in r else "ℹ️"))
                    st.markdown(f"<div style='font-size:0.78rem;color:var(--muted);padding:2px 0;'>{ico} {r}</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Quick trade button
                if pr > 0 and sig_d["signal"] in ("BUY", "STRONG BUY"):
                    if st.button(f"🚀 BUY {sel_row['strike']} {otype}", key=f"buy_deep_{otype}_{sel_row['strike']}"):
                        lots    = kelly_lots(float(base_lot_cap), st.session_state.kelly_wr, 1.5, sig_d["strength"], pr * lot) if use_kelly else 1
                        cost    = fno_trade_cost(pr, lots, lot, "BUY")
                        trade   = {
                            "id":           f"{chain_idx}{sel_row['strike']}{otype}_{int(time.time())}",
                            "index":        chain_idx,
                            "strike":       sel_row["strike"],
                            "type":         otype,
                            "expiry":       str(exp_date),
                            "entry_price":  pr,
                            "cmp":          pr,
                            "lots":         lots,
                            "lot_size":     lot,
                            "invested":     round(pr * lots * lot, 2),
                            "brokerage":    cost,
                            "sl":           sl,
                            "targets":      tgts,
                            "pb_levels":    [pb1, pb2, pb3],
                            "trail_at":     pb4,
                            "trailing_sl":  None,
                            "pnl":          0.0,
                            "status":       "OPEN",
                            "entry_time":   datetime.now().strftime("%H:%M:%S"),
                            "entry_dt":     datetime.now(),
                            "signal":       sig_d["signal"],
                            "strength":     sig_d["strength"],
                            "delta":        dlt,
                            "theta":        tht,
                            "days_exp":     sel_row["days_exp"],
                        }
                        st.session_state.portfolio.append(trade)
                        st.success(f"✅ BUY {lots} lot(s) {chain_idx} {sel_row['strike']} {otype} @ ₹{pr:.2f}")

    else:
        st.info(f"👆 Click 'Load {chain_idx} Option Chain' to build the live chain with signals.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Signal Scanner
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sec-title">⚡ OPTION SIGNAL SCANNER — BEST BUY SETUPS</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns([1, 1])
    with sc1:
        scan_index = st.multiselect("Scan Index", ["BANKNIFTY", "NIFTY50"], default=["BANKNIFTY", "NIFTY50"])
    with sc2:
        scan_filter = st.selectbox("Show", ["ALL", "CE Only", "PE Only", "STRONG BUY Only"])

    if st.button("🔭 Scan for Best Option Signals", use_container_width=True):
        all_sigs = []
        with st.spinner("Scanning option chains…"):
            for idx_name in scan_index:
                spot_s = bn_spot if idx_name == "BANKNIFTY" else nf_spot
                exp_s  = exp_bn  if idx_name == "BANKNIFTY" else exp_nf
                sigs   = scan_option_signals(idx_name, spot_s, vix_val, exp_s, n_strikes)
                all_sigs.extend(sigs)
        all_sigs.sort(key=lambda x: -x["strength"])
        st.session_state.scan_results = all_sigs

    results = st.session_state.get("scan_results", [])

    if results:
        # Filter
        if scan_filter == "CE Only":    results = [r for r in results if r["type"] == "CE"]
        elif scan_filter == "PE Only":  results = [r for r in results if r["type"] == "PE"]
        elif scan_filter == "STRONG BUY Only": results = [r for r in results if r["signal"] == "STRONG BUY"]

        # Summary metrics
        c1, c2, c3, c4, c5 = st.columns(5)
        ce_sigs  = [r for r in results if r["type"] == "CE"]
        pe_sigs  = [r for r in results if r["type"] == "PE"]
        str_buys = [r for r in results if r["signal"] == "STRONG BUY"]
        avg_str  = np.mean([r["strength"] for r in results]) if results else 0

        c1.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--cyan)">{len(results)}</div><div class="m-lbl">Total Signals</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--ce-color)">{len(ce_sigs)}</div><div class="m-lbl">CE Signals</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="m-card"><div class="m-val" style="color:#ff4081">{len(pe_sigs)}</div><div class="m-lbl">PE Signals</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--green)">{len(str_buys)}</div><div class="m-lbl">Strong Buys</div></div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--accent)">{avg_str:.0f}%</div><div class="m-lbl">Avg Strength</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Signal cards
        for sig in results:
            if sig["strength"] < min_sig_str:
                continue
            otype_color = "var(--ce-color)" if sig["type"] == "CE" else "#ff4081"
            atm_tag     = " 🎯" if sig.get("is_atm") else ""
            lot = sig["lot"]
            tgts = sig["targets"]

            with st.expander(
                f"{'🔵' if sig['type']=='CE' else '🔴'} {sig['index']} {sig['strike']:,} {sig['type']}{atm_tag} | "
                f"₹{sig['price']:.2f} | {sig['signal']} | Str: {sig['strength']}% | "
                f"Δ={sig['delta']:.3f} | θ={sig['theta']:.2f}"
            ):
                ec1, ec2, ec3, ec4 = st.columns(4)
                ec1.metric("Premium",   f"₹{sig['price']:.2f}")
                ec2.metric("Stop Loss", f"₹{sig['sl']:.2f}")
                ec3.metric(f"T1 (+{tgts[0]['pct']}%)", f"₹{tgts[0]['price']:.2f}")
                ec4.metric(f"T2 (+{tgts[1]['pct']}%)", f"₹{tgts[1]['price']:.2f}")

                # Greeks
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0;">
                    <div class="greek-box"><div class="greek-val" style="color:{otype_color}">{sig['delta']:.4f}</div><div class="greek-lbl">Delta</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--purple)">{sig['gamma']:.5f}</div><div class="greek-lbl">Gamma</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--red)">{sig['theta']:.2f}</div><div class="greek-lbl">Theta/day</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--green)">{sig['vega']:.2f}</div><div class="greek-lbl">Vega</div></div>
                    <div class="greek-box"><div class="greek-val" style="color:var(--accent)">{sig['iv']}%</div><div class="greek-lbl">Est. IV</div></div>
                </div>""", unsafe_allow_html=True)

                # Profit booking
                st.markdown("**📊 Staged Profit Booking Plan**")
                for t in tgts:
                    profit_pts = t["price"] - sig["price"]
                    profit_lots = profit_pts * lot
                    st.markdown(f"""<div class="pb-row">
                        <span class="pb-pct">+{t['pct']}%</span>
                        <span class="pb-price">₹{t['price']:.2f}</span>
                        <span class="pb-action">{t['label']}</span>
                        <span style="font-family:'Space Mono';font-size:0.8rem;color:var(--green);">+₹{profit_lots:.0f}/lot</span>
                    </div>""", unsafe_allow_html=True)

                # Reasons
                st.markdown("**💡 Signal Reasoning**")
                for r in sig["reasons"][:5]:
                    st.markdown(f"<div style='font-size:0.8rem;color:var(--muted);padding:2px 0;'>• {r}</div>", unsafe_allow_html=True)

                # Trade button
                if st.button(f"🚀 BUY {sig['index']} {sig['strike']} {sig['type']}", key=f"scan_buy_{sig['index']}_{sig['strike']}_{sig['type']}"):
                    pr   = sig["price"]
                    lots = kelly_lots(float(base_lot_cap), st.session_state.kelly_wr, 1.5, sig["strength"], pr * lot) if use_kelly else 1
                    cost = fno_trade_cost(pr, lots, lot, "BUY")
                    trade = {
                        "id":           f"{sig['index']}{sig['strike']}{sig['type']}_{int(time.time())}",
                        "index":        sig["index"],
                        "strike":       sig["strike"],
                        "type":         sig["type"],
                        "expiry":       str(sig["expiry"]),
                        "entry_price":  pr,
                        "cmp":          pr,
                        "lots":         lots,
                        "lot_size":     lot,
                        "invested":     round(pr * lots * lot, 2),
                        "brokerage":    cost,
                        "sl":           sig["sl"],
                        "targets":      tgts,
                        "pb_levels":    [pb1, pb2, pb3],
                        "trail_at":     pb4,
                        "trailing_sl":  None,
                        "pnl":          0.0,
                        "status":       "OPEN",
                        "entry_time":   datetime.now().strftime("%H:%M:%S"),
                        "entry_dt":     datetime.now(),
                        "signal":       sig["signal"],
                        "strength":     sig["strength"],
                        "delta":        sig["delta"],
                        "theta":        sig["theta"],
                        "days_exp":     sig["days_exp"],
                    }
                    st.session_state.portfolio.append(trade)
                    st.success(f"✅ Bought {lots} lot(s) @ ₹{pr:.2f}")
    else:
        st.info("👆 Click Scan to find the best CE/PE signals across BankNifty & Nifty50.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Auto Trading
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="sec-title">🤖 AUTO OPTIONS TRADING ENGINE</div>', unsafe_allow_html=True)

    if vix_val > 25:
        st.markdown('<div class="warn-box">⚠️ VIX > 25 — Auto trading paused. Market too volatile for option buying.</div>', unsafe_allow_html=True)

    if not st.session_state.auto_trading:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1117,#111827);border:1px solid var(--accent);
             border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">
            <div style="font-family:'Bebas Neue';font-size:2rem;color:var(--accent);letter-spacing:3px;">AI OPTIONS AUTO TRADER</div>
            <div style="color:var(--muted);font-size:0.85rem;margin-top:8px;">
                Scans BankNifty + Nifty50 · Best CE/PE strikes · Kelly sizing · Staged profit booking · Auto SL
            </div>
        </div>""", unsafe_allow_html=True)

        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            a_dur  = st.number_input("⏱️ Duration (minutes)", 1, 390, 30, 5)
            a_cap  = st.number_input("💰 Capital per trade (₹)", 5000, 200000, 10000, 2500)
            a_max  = st.number_input("📊 Max simultaneous positions", 1, 10, 3, 1)
            a_str  = st.number_input("🎯 Min signal strength (%)", 50, 90, 60, 5)
            a_idx  = st.multiselect("🔭 Scan", ["BANKNIFTY", "NIFTY50"], default=["BANKNIFTY", "NIFTY50"])

            mood_label = f"🐂 BULLISH — prefer CE" if idx_sig == "BULLISH" else (f"🐻 BEARISH — prefer PE" if idx_sig == "BEARISH" else "↔️ SIDEWAYS — balanced")
            st.markdown(f'<div class="info-box">Market Bias: <b>{mood_label}</b></div>', unsafe_allow_html=True)

            if vix_val <= 25:
                if st.button("🚀 START AUTO TRADING", use_container_width=True):
                    st.session_state.auto_trading = True
                    st.session_state.auto_end     = datetime.now() + timedelta(minutes=int(a_dur))
                    st.session_state.auto_log     = []
                    st.session_state.auto_pnl     = 0.0
                    st.session_state._auto_dur    = int(a_dur)
                    st.session_state._auto_cap    = float(a_cap)
                    st.session_state._auto_max    = int(a_max)
                    st.session_state._auto_str    = int(a_str)
                    st.session_state._auto_idx    = a_idx
                    st.rerun()
            else:
                st.error("🚫 VIX too high — auto trading blocked.")
    else:
        end_t    = st.session_state.auto_end
        rem      = max(0.0, (end_t - datetime.now()).total_seconds())
        total_s  = st.session_state._auto_dur * 60
        progress = (total_s - rem) / total_s if total_s > 0 else 1.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⏱️ Time Left",    f"{int(rem//60)}m {int(rem%60)}s")
        c2.metric("Open Positions",  len(st.session_state.portfolio))
        live_pnl = sum(p.get("pnl", 0) for p in st.session_state.portfolio)
        c3.metric("Live P&L",        f"₹{live_pnl:,.0f}", delta="▲" if live_pnl >= 0 else "▼")
        c4.metric("Realized P&L",    f"₹{sum(p.get('pnl',0) for p in st.session_state.history):,.0f}")
        st.progress(min(progress, 1.0))

        if rem <= 0:
            # Square off
            st.warning("⏰ Session ended — squaring off all positions!")
            closed   = []
            tot_pnl  = 0.0
            for pos in st.session_state.portfolio:
                ep     = float(pos.get("entry_price", 0))
                lots   = int(pos.get("lots", 1))
                ls     = int(pos.get("lot_size", NIFTY_LOT))
                cmp    = pos.get("cmp", ep)
                gross  = (cmp - ep) * lots * ls
                net    = gross - float(pos.get("brokerage", 0))
                tot_pnl += net
                closed.append({**pos, "exit_price": cmp, "pnl": round(net, 2), "status": "CLOSED", "exit_time": datetime.now().strftime("%H:%M:%S")})
                st.session_state.journal.append({"type": pos["type"], "pnl": round(net, 2), "win": net >= 0, "strength": pos.get("strength", 0), "date": datetime.now().strftime("%Y-%m-%d")})
            st.session_state.history.extend(closed)
            st.session_state.portfolio  = []
            st.session_state.auto_trading = False
            if st.session_state.journal:
                wins = sum(1 for j in st.session_state.journal if j["win"])
                st.session_state.kelly_wr = wins / len(st.session_state.journal)
            st.rerun()
        else:
            _max = st.session_state.get("_auto_max", 3)
            _str = st.session_state.get("_auto_str", 60)
            _cap = st.session_state.get("_auto_cap", 10000.0)
            _idx = st.session_state.get("_auto_idx", ["BANKNIFTY"])

            if len(st.session_state.portfolio) < _max and vix_val <= 25:
                with st.spinner("Scanning for signals…"):
                    all_new = []
                    for idx_nm in _idx:
                        spot_s = bn_spot if idx_nm == "BANKNIFTY" else nf_spot
                        exp_s  = exp_bn  if idx_nm == "BANKNIFTY" else exp_nf
                        sigs   = scan_option_signals(idx_nm, spot_s, vix_val, exp_s, 6)
                        # Bias filter
                        for sig in sigs:
                            if sig["strength"] < _str:
                                continue
                            if idx_sig == "BULLISH" and sig["type"] == "PE":
                                continue
                            if idx_sig == "BEARISH" and sig["type"] == "CE":
                                continue
                            all_new.append(sig)

                existing = {f"{p['index']}{p['strike']}{p['type']}" for p in st.session_state.portfolio}
                for sig in sorted(all_new, key=lambda x: -x["strength"]):
                    if len(st.session_state.portfolio) >= _max:
                        break
                    key = f"{sig['index']}{sig['strike']}{sig['type']}"
                    if key in existing:
                        continue
                    lot  = sig["lot"]
                    pr   = sig["price"]
                    lots = kelly_lots(_cap, st.session_state.kelly_wr, 1.5, sig["strength"], pr * lot) if use_kelly else 1
                    cost = fno_trade_cost(pr, lots, lot, "BUY")
                    trade = {
                        "id":           f"{sig['index']}{sig['strike']}{sig['type']}_{int(time.time()*1000)}",
                        "index":        sig["index"],
                        "strike":       sig["strike"],
                        "type":         sig["type"],
                        "expiry":       str(sig["expiry"]),
                        "entry_price":  pr,
                        "cmp":          pr,
                        "lots":         lots,
                        "lot_size":     lot,
                        "invested":     round(pr * lots * lot, 2),
                        "brokerage":    cost,
                        "sl":           sig["sl"],
                        "targets":      sig["targets"],
                        "pb_levels":    [pb1, pb2, pb3],
                        "trail_at":     pb4,
                        "trailing_sl":  None,
                        "pnl":          0.0,
                        "status":       "OPEN",
                        "entry_time":   datetime.now().strftime("%H:%M:%S"),
                        "entry_dt":     datetime.now(),
                        "signal":       sig["signal"],
                        "strength":     sig["strength"],
                        "delta":        sig["delta"],
                        "theta":        sig["theta"],
                        "days_exp":     sig["days_exp"],
                    }
                    st.session_state.portfolio.append(trade)
                    st.session_state.auto_log.append(trade)
                    existing.add(key)

            # Update P&L and check exits
            still_open = []
            for pos in st.session_state.portfolio:
                ep      = float(pos.get("entry_price", 0))
                lots    = int(pos.get("lots", 1))
                ls      = int(pos.get("lot_size", NIFTY_LOT))
                # Simulate price movement (in real app, fetch from live feed)
                # For now, use entry price with small random walk
                cmp     = pos.get("cmp", ep)
                gross   = (cmp - ep) * lots * ls
                net_pnl = gross - float(pos.get("brokerage", 0))
                pos["pnl"] = round(net_pnl, 2)

                # Trailing stop
                pnl_pct = (cmp - ep) / ep * 100 if ep > 0 else 0
                if pnl_pct >= pos.get("trail_at", pb4):
                    if pos.get("trailing_sl") is None:
                        pos["trailing_sl"] = ep  # move to breakeven
                    else:
                        new_trail = cmp * 0.95
                        if new_trail > pos["trailing_sl"]:
                            pos["trailing_sl"] = round(new_trail, 2)

                eff_sl    = pos.get("trailing_sl") or pos.get("sl", ep * 0.5)
                hit_sl    = cmp <= eff_sl
                hit_tgt   = cmp >= pos["targets"][2]["price"]
                time_exit = use_time_x and (datetime.now() - pos.get("entry_dt", datetime.now())).total_seconds() > 1800 and abs(pnl_pct) < 5

                if hit_sl or hit_tgt or time_exit:
                    cost2   = fno_trade_cost(cmp, lots, ls, "SELL")
                    fin_pnl = gross - float(pos.get("brokerage", 0)) - cost2
                    st.session_state.history.append({**pos, "exit_price": cmp, "pnl": round(fin_pnl, 2), "status": "CLOSED", "exit_time": datetime.now().strftime("%H:%M:%S")})
                    st.session_state.journal.append({"type": pos["type"], "pnl": round(fin_pnl, 2), "win": fin_pnl >= 0, "strength": pos.get("strength", 0), "date": datetime.now().strftime("%Y-%m-%d")})
                else:
                    still_open.append(pos)
            st.session_state.portfolio = still_open

            # Display positions
            st.markdown("### 📊 Open Positions")
            if st.session_state.portfolio:
                for pos in st.session_state.portfolio:
                    pnl     = pos.get("pnl", 0)
                    trail   = f" | Trail SL: ₹{pos['trailing_sl']:.2f}" if pos.get("trailing_sl") else ""
                    color   = "var(--green)" if pnl >= 0 else "var(--red)"
                    otype_c = "var(--ce-color)" if pos["type"] == "CE" else "#ff4081"
                    st.markdown(f"""
                    <div class="trade-card {'win-card' if pnl>=0 else 'loss-card'}">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                            <div>
                                <span style="font-family:'Bebas Neue';font-size:1.2rem;color:{otype_c};">{pos['index']} {pos['strike']:,} {pos['type']}</span>
                                <span style="font-size:0.75rem;color:var(--muted);margin-left:10px;">Exp: {pos['expiry']} · {pos['lots']} lot(s) · Str: {pos.get('strength',0)}%</span>
                            </div>
                            <div style="font-family:'Space Mono';font-size:1rem;color:{color};font-weight:700;">₹{pnl:+,.0f}{trail}</div>
                        </div>
                        <div style="display:flex;gap:12px;margin-top:8px;font-family:'Space Mono';font-size:0.8rem;color:var(--muted);">
                            <span>Entry: ₹{pos['entry_price']:.2f}</span>
                            <span>SL: ₹{pos['sl']:.2f}</span>
                            <span>T1: ₹{pos['targets'][0]['price']:.2f}</span>
                            <span>T2: ₹{pos['targets'][1]['price']:.2f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No open positions. Scanning next cycle…")

            col_stp, _ = st.columns([1, 3])
            with col_stp:
                if st.button("🛑 STOP & SQUARE OFF", use_container_width=True):
                    for pos in st.session_state.portfolio:
                        ep   = float(pos["entry_price"])
                        lots = int(pos["lots"])
                        ls   = int(pos["lot_size"])
                        cmp  = pos.get("cmp", ep)
                        gross = (cmp - ep) * lots * ls
                        net   = gross - float(pos.get("brokerage", 0))
                        st.session_state.history.append({**pos, "exit_price": cmp, "pnl": round(net, 2), "status": "CLOSED"})
                        st.session_state.journal.append({"type": pos["type"], "pnl": round(net, 2), "win": net >= 0, "strength": pos.get("strength", 0), "date": datetime.now().strftime("%Y-%m-%d")})
                    st.session_state.portfolio    = []
                    st.session_state.auto_trading = False
                    st.rerun()

            time.sleep(15)
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Portfolio
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="sec-title">💼 LIVE OPTIONS PORTFOLIO</div>', unsafe_allow_html=True)

    if not st.session_state.portfolio:
        st.info("No open positions.")
    else:
        total_pnl = sum(p.get("pnl", 0) for p in st.session_state.portfolio)
        total_inv = sum(p.get("invested", 0) for p in st.session_state.portfolio)
        total_brk = sum(p.get("brokerage", 0) for p in st.session_state.portfolio)

        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--cyan)">₹{total_inv:,.0f}</div><div class="m-lbl">Invested</div></div>', unsafe_allow_html=True)
        pnl_c = "var(--green)" if total_pnl >= 0 else "var(--red)"
        pc2.markdown(f'<div class="m-card"><div class="m-val" style="color:{pnl_c}">₹{total_pnl:+,.0f}</div><div class="m-lbl">Unrealised P&L</div></div>', unsafe_allow_html=True)
        ret_pct = total_pnl / total_inv * 100 if total_inv > 0 else 0
        pc3.markdown(f'<div class="m-card"><div class="m-val" style="color:{pnl_c}">{ret_pct:+.1f}%</div><div class="m-lbl">Return %</div></div>', unsafe_allow_html=True)
        pc4.markdown(f'<div class="m-card"><div class="m-val" style="color:var(--accent)">₹{total_brk:,.0f}</div><div class="m-lbl">Charges</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        for pos in st.session_state.portfolio:
            pnl     = pos.get("pnl", 0)
            otype_c = "var(--ce-color)" if pos["type"] == "CE" else "#ff4081"
            pnl_c   = "var(--green)" if pnl >= 0 else "var(--red)"
            trail   = pos.get("trailing_sl")

            with st.expander(
                f"{'🔵' if pos['type']=='CE' else '🔴'} {pos['index']} {pos['strike']:,} {pos['type']} | "
                f"Entry ₹{pos['entry_price']:.2f} | {pos['lots']} lot(s) | P&L: ₹{pnl:+,.0f}"
            ):
                p1, p2, p3, p4, p5, p6 = st.columns(6)
                p1.metric("Entry",  f"₹{pos['entry_price']:.2f}")
                p2.metric("CMP",    f"₹{pos.get('cmp', pos['entry_price']):.2f}")
                p3.metric("Lots",   pos["lots"])
                p4.metric("SL",     f"₹{pos['sl']:.2f}")
                p5.metric("Net P&L",f"₹{pnl:+,.0f}")
                p6.metric("Delta",  f"{pos.get('delta',0):.4f}")

                if trail:
                    st.markdown(f'<div class="success-box">🎯 Trailing SL Active: ₹{trail:,.2f} — locked in profit</div>', unsafe_allow_html=True)

                st.markdown("**📊 Profit Booking Targets**")
                for t in pos.get("targets", []):
                    profit_pts = t["price"] - pos["entry_price"]
                    profit_lot = profit_pts * pos["lot_size"]
                    st.markdown(f"""<div class="pb-row">
                        <span class="pb-pct">+{t['pct']}%</span>
                        <span class="pb-price">₹{t['price']:.2f}</span>
                        <span class="pb-action">{t['label']}</span>
                        <span style="font-family:'Space Mono';font-size:0.8rem;color:var(--green);">+₹{profit_lot*pos['lots']:.0f} total</span>
                    </div>""", unsafe_allow_html=True)

                if st.button("✅ Square Off", key=f"sq_{pos['id']}"):
                    ep   = float(pos["entry_price"])
                    lots = int(pos["lots"])
                    ls   = int(pos["lot_size"])
                    cmp  = pos.get("cmp", ep)
                    cost2 = fno_trade_cost(cmp, lots, ls, "SELL")
                    gross = (cmp - ep) * lots * ls
                    fin   = gross - float(pos.get("brokerage", 0)) - cost2
                    st.session_state.history.append({**pos, "exit_price": cmp, "pnl": round(fin, 2), "status": "CLOSED", "exit_time": datetime.now().strftime("%H:%M:%S")})
                    st.session_state.journal.append({"type": pos["type"], "pnl": round(fin, 2), "win": fin >= 0, "strength": pos.get("strength", 0), "date": datetime.now().strftime("%Y-%m-%d")})
                    st.session_state.portfolio = [p for p in st.session_state.portfolio if p["id"] != pos["id"]]
                    if st.session_state.journal:
                        wins = sum(1 for j in st.session_state.journal if j["win"])
                        st.session_state.kelly_wr = wins / len(st.session_state.journal)
                    st.success(f"Squared off @ ₹{cmp:.2f} | Net: ₹{fin:+,.0f}")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — History
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="sec-title">📜 TRADE HISTORY</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No closed trades yet.")
    else:
        hist    = st.session_state.history
        wins    = len([t for t in hist if t.get("pnl", 0) >= 0])
        losses  = len(hist) - wins
        net_pnl = sum(t.get("pnl", 0) for t in hist)
        win_r   = wins / len(hist) * 100 if hist else 0
        avg_win = np.mean([t["pnl"] for t in hist if t.get("pnl",0)>=0]) if wins else 0
        avg_los = np.mean([t["pnl"] for t in hist if t.get("pnl",0)<0]) if losses else 0

        hc1, hc2, hc3, hc4, hc5, hc6 = st.columns(6)
        hc1.metric("Total Trades", len(hist))
        hc2.metric("Winners",      wins)
        hc3.metric("Losers",       losses)
        hc4.metric("Win Rate",     f"{win_r:.1f}%")
        hc5.metric("Net P&L",      f"₹{net_pnl:+,.0f}")
        hc6.metric("Avg Win/Loss", f"₹{avg_win:.0f} / ₹{avg_los:.0f}")

        df_h = pd.DataFrame(hist)
        disp_cols = [c for c in ["index","strike","type","entry_price","exit_price","lots","invested","pnl","status","entry_time","exit_time"] if c in df_h.columns]
        st.dataframe(df_h[disp_cols].rename(columns={"entry_price":"Entry(₹)","exit_price":"Exit(₹)","pnl":"Net P&L(₹)"}), use_container_width=True, hide_index=True)

        if len(hist) >= 2:
            df_h["cumulative"] = df_h["pnl"].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=df_h["cumulative"], mode="lines+markers",
                line=dict(color="#f0b429", width=2),
                fill="tozeroy", fillcolor="rgba(240,180,41,0.08)",
                marker=dict(color=["#00e676" if p >= 0 else "#ff1744" for p in df_h["pnl"]], size=8)
            ))
            fig.update_layout(
                title="Cumulative P&L",
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                font=dict(color="#cdd5e0", family="Barlow Condensed"),
                xaxis=dict(gridcolor="#1c2333"), yaxis=dict(gridcolor="#1c2333"),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

            if "type" in df_h.columns:
                type_pnl = df_h.groupby("type")["pnl"].sum().reset_index()
                fig2 = px.bar(type_pnl, x="type", y="pnl", color="type",
                              color_discrete_map={"CE": "#00e5ff", "PE": "#ff4081"},
                              title="P&L by Option Type")
                fig2.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                                   font=dict(color="#cdd5e0"), height=250)
                st.plotly_chart(fig2, use_container_width=True)

        st.download_button("📥 Download History CSV", data=df_h.to_csv(index=False),
                           file_name=f"options_history_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Journal
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="sec-title">📓 TRADE JOURNAL & ANALYTICS</div>', unsafe_allow_html=True)

    journal = st.session_state.journal
    if not journal:
        st.info("No journal entries yet.")
    else:
        jdf = pd.DataFrame(journal)
        if "pnl" in jdf.columns:
            # CE vs PE breakdown
            if "type" in jdf.columns:
                st.markdown("#### CE vs PE Performance")
                tp = jdf.groupby("type").agg(total=("pnl","sum"), trades=("pnl","count"), win_rate=("win","mean")).reset_index()
                tp["win_rate"] = (tp["win_rate"] * 100).round(1)
                st.dataframe(tp.rename(columns={"type":"Type","total":"Net P&L","trades":"Trades","win_rate":"Win Rate %"}), use_container_width=True, hide_index=True)

            # Strength buckets
            if "strength" in jdf.columns:
                jdf["str_bucket"] = pd.cut(jdf["strength"], bins=[0,55,65,75,85,100],
                                            labels=["50-55","55-65","65-75","75-85","85+"])
                st.markdown("#### P&L by Signal Strength")
                sb = jdf.groupby("str_bucket", observed=True).agg(total=("pnl","sum"), trades=("pnl","count"), win_rate=("win","mean")).reset_index()
                sb["win_rate"] = (sb["win_rate"] * 100).round(1)
                fig3 = px.bar(sb, x="str_bucket", y="total", color="win_rate",
                              color_continuous_scale=["#ff1744","#ffd600","#00e676"],
                              title="P&L by Signal Strength Bucket",
                              labels={"str_bucket":"Strength","total":"P&L (₹)"})
                fig3.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#cdd5e0"), height=280)
                st.plotly_chart(fig3, use_container_width=True)

        kelly_wr = st.session_state.kelly_wr
        st.markdown(f'<div class="info-box">🧮 Current Kelly Win Rate: <b>{kelly_wr*100:.1f}%</b> from {len(journal)} trades — dynamically adjusting position sizing</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear Journal"):
            st.session_state.journal   = []
            st.session_state.kelly_wr  = 0.55
            st.rerun()
