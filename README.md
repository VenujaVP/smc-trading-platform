# 🚀 SMC Trading Platform - Professional Edition

**Advanced Multi-Timeframe Smart Money Concepts Trading System**  
*Complete GUI Dashboard • Real-Time Visualization • Automated Trading • Professional-Grade Software*

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dashboard Guide](#dashboard-guide)
- [Configuration](#configuration)
- [Trading Logic](#trading-logic)
- [Security](#security)
- [Screenshots](#screenshots)

---

## 🎯 Overview

A **professional-grade algorithmic trading platform** that implements Smart Money Concepts (SMC) across multiple timeframes with a complete GUI dashboard for visualization, monitoring, and management.

### Key Highlights

✅ **Real-Time Market Visualization** - Interactive candlestick charts with market structure overlay  
✅ **Multi-Timeframe Analysis** - Synchronized 4H, 1H, and 15m analysis  
✅ **Professional Dashboard** - Modern dark theme with sidebar navigation  
✅ **Secure Settings Management** - Encrypted credential storage  
✅ **Complete Trading Management** - Positions, history, performance analytics  
✅ **Automated Trading Engine** - Background execution with state persistence  
✅ **Order Block Precision** - Institutional entry point detection  

---

## 🎨 Features

### 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Real-time overview, account stats, market structure chart, open positions |
| **Live Analysis** | Multi-timeframe chart analysis (HTF, Minor, Entry) |
| **Trading Panel** | Manual trade execution and quick actions |
| **Trade History** | Complete history with filtering and export |
| **Performance** | Analytics, win rate, R:R ratio, equity curve |
| **Settings** | MT5 connection, trading parameters, system configuration |
| **Alerts** | Real-time notifications and system events |

### 🔧 Core Functionality

- **Market Structure Detection**
  - Pivot High/Low calculation (customizable lookback)
  - Body-based Break of Structure (BOS) detection
  - Dynamic range tracking (Main & Minor)
  - Equilibrium zone identification

- **Entry Logic**
  - Order Block detection
  - Fair Value Gap (FVG) analysis
  - Precise limit order placement
  - R:R validation (minimum 1:3)

- **Risk Management**
  - Automatic position sizing (1% account risk)
  - Structural stop loss placement
  - External liquidity take profit targeting
  - Margin usage monitoring

---

## 🏗️ System Architecture

```
smc-trading-platform/
├── gui/                          # Dashboard Application
│   ├── app.py                    # Main Dash app with sidebar
│   ├── pages/                    # Navigation pages
│   │   ├── dashboard_page.py     # Main dashboard
│   │   ├── analysis_page.py      # Live multi-TF analysis
│   │   ├── trading_page.py       # Manual trading panel
│   │   ├── history_page.py       # Trade history
│   │   ├── performance_page.py   # Analytics & stats
│   │   ├── settings_page.py      # Complete settings UI
│   │   └── alerts_page.py        # Notifications
│   └── utils/                    # Utility modules
│       ├── settings_manager.py   # Secure config storage
│       ├── mt5_interface.py      # MT5 bridge
│       └── chart_builder.py      # Plotly chart creation
│
├── config.py                     # Configuration module
├── data_feed.py                  # MT5 data retrieval
├── state_machine.py              # Trading state (OOP)
├── structure_engine.py           # Market structure logic
├── execution.py                  # Order execution & risk
├── main.py                       # Trading engine loop
├── launch.py                     # Application launcher
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 📦 Installation

### Prerequisites

1. **Python 3.10+**
2. **MetaTrader 5** installed and running
3. **MT5 Account** with API access

### Setup Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the platform
python launch.py
```

### First-Time Configuration

1. Select option **1** (Dashboard Only)
2. Navigate to **Settings** page
3. Configure **MT5 Connection**:
   - Account Number
   - Password
   - Server
   - Symbol (e.g., XAUUSD)
4. Click **Test Connection**
5. Click **Save MT5 Settings**
6. Configure **Trading Parameters** (risk%, R:R, etc.)
7. Restart with option **3** (Complete System)

---

## 🚀 Quick Start

### Launch Options

```bash
python launch.py
```

**Menu:**
- `1` - Dashboard Only (configuration & monitoring)
- `2` - Trading Engine Only (headless automated trading)
- `3` - Complete System (dashboard + engine)
- `4` - Exit

### Access Dashboard

Open browser: **http://127.0.0.1:8050**

---

## 📱 Dashboard Guide

### 🏠 Main Dashboard

- **Account Overview Cards**
  - Balance, Equity, Margin Usage, Daily P/L
  
- **Market Structure Chart**
  - Real-time candlestick chart (4H)
  - Main Range (High, Low, EQ) overlays
  - Watch Pivot markers
  - Entry setup visualization (Entry, SL, TP)

- **Trading State Panel**
  - Current market bias (Bullish/Bearish/Neutral)
  - Trading phase
  - Range levels
  - Minor structure status
  - Entry setup details

- **Open Positions Table**
  - Live position monitoring
  - P/L tracking

- **Activity Log**
  - Recent system events

### ⚙️ Settings Page

#### MT5 Connection Tab
- Account credentials (encrypted storage)
- Test connection before saving
- Symbol configuration

#### Trading Parameters Tab
- Timeframe selection (HTF, Conf, Minor, Entry)
- Pivot lookback periods
- Risk management (risk%, min R:R, SL buffer)

#### System Tab
- Refresh intervals
- Logging level
- Magic number
- Auto-trading toggle
- Notifications

---

## 🔐 Security

### Credential Encryption

All sensitive data (passwords, account numbers) are:
- Encrypted using **Fernet** (symmetric encryption)
- Stored in `config/credentials.enc`
- Decrypted only at runtime
- Never logged or displayed

### Key Management

Encryption key stored in `config/.key` (add to `.gitignore`)

---

## 📈 Trading Logic Pipeline

### Phase 1: Main Structure (HTF - 4H)
1. Calculate Pivot Highs/Lows (5-candle lookback)
2. Detect Main BOS (body closes above/below pivot)
3. Establish Main Range (confirmed + unconfirmed)
4. Calculate Equilibrium (50% level)

### Phase 2: Pullback (1H)
1. Wait for wick to touch EQ zone
2. Identify Watch Pivot (recent 1H pivot)
3. Track extreme (lowest low / highest high)

### Phase 3: Minor MSS (1H)
1. Body closes above/below Watch Pivot
2. Lock tracked extreme as Minor Confirmed Level

### Phase 4: Entry (15m)
1. Identify Order Block (last opposing candle)
2. Calculate entry at OB open
3. Set SL below/above Minor Level + buffer
4. Set TP at Main Range extreme
5. Validate R:R (minimum 1:3)
6. Calculate position size (1% risk)
7. Place Limit Order

---

## 📊 Configuration Examples

### Conservative Settings
```yaml
trading:
  risk_percent: 0.5
  min_risk_reward: 4.0
  stop_loss_buffer_pips: 30
```

### Aggressive Settings
```yaml
trading:
  risk_percent: 2.0
  min_risk_reward: 2.0
  stop_loss_buffer_pips: 10
```

---

## 🎨 Screenshots

### Dashboard Overview
*(Professional dark theme with real-time charts)*

### Settings Page
*(Secure credential management)*

### Market Structure Chart
*(Candlesticks + structure overlays)*

---

## ⚠️ Disclaimer

**This software is for educational and informational purposes only.**

- Trading involves substantial risk of loss
- Past performance does not indicate future results
- Always test on demo accounts first
- The developers assume no liability for financial losses

---

## 📞 Support

For issues:
1. Check `smc_platform.log` for detailed traces
2. Verify MT5 connection in Settings
3. Test individual modules (`python data_feed.py`)

---

## 🔄 Updates & Roadmap

- [x] Complete GUI Dashboard
- [x] Real-time market visualization
- [x] Secure settings management
- [x] Multi-timeframe analysis
- [x] Automated trading engine
- [ ] Backtesting module
- [ ] Trade analytics export
- [ ] Mobile notifications
- [ ] Multi-symbol support

---

## 📜 License

**Commercial License - Professional Edition**

© 2024 SMC Trading Platform. All rights reserved.

---

**Built with:** Python • Dash • Plotly • MetaTrader5 • pandas • cryptography

**Version:** 1.0.0 Professional Edition  
**Last Updated:** November 2024
