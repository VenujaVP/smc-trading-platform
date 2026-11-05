# 🚀 Quick Start Guide - SMC Trading Platform Professional Edition

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Launch the Platform

```bash
python launch.py
```

### Step 3: Choose Launch Mode

You'll see:
```
1. Dashboard Only (Visualization & Settings)
2. Trading Engine Only (Automated Trading)
3. Complete System (Dashboard + Trading Engine)
4. Exit
```

**For first-time setup, choose Option 1**

### Step 4: Configure MT5 Connection

1. Open browser: **http://127.0.0.1:8050**
2. Navigate to **Settings** page (sidebar)
3. Click **MT5 Connection** tab
4. Enter your credentials:
   - Account Number
   - Password
   - Server
   - Symbol (e.g., XAUUSD)
5. Click **Test Connection**
6. If successful, click **Save MT5 Settings**

### Step 5: Configure Trading Parameters

1. Click **Trading Parameters** tab
2. Adjust settings:
   - **Risk Per Trade**: 1.0% (recommended)
   - **Minimum R:R**: 3.0 (1:3 ratio)
   - **Stop Loss Buffer**: 20 pips
3. Click **Save Trading Parameters**

### Step 6: Start Live Trading

1. Restart the platform: `python launch.py`
2. Choose **Option 3** (Complete System)
3. Dashboard opens at http://127.0.0.1:8050
4. Trading engine runs in background

---

## 📱 Dashboard Navigation

### 🏠 Dashboard
- **Real-time account overview**
- **Market structure chart** with all levels
- **Trading state panel** (bias, phase, ranges)
- **Open positions** table
- **Recent activity** log

### 📊 Live Analysis
- **Multi-timeframe charts** (4H, 1H, 15m)
- **Synchronized analysis** across timeframes

### 🎛️ Trading Panel
- **Manual trade entry**
- **Quick actions** (close all, cancel orders)
- **Current price display**

### 📜 Trade History
- **Complete trade log**
- **Filter by date/type**
- **Export functionality**

### 📈 Performance
- **Win rate statistics**
- **Average R:R ratio**
- **Equity curve chart**
- **Total profit/loss**

### ⚙️ Settings
- **MT5 Connection** (secure credential storage)
- **Trading Parameters** (timeframes, risk, pivots)
- **System Settings** (refresh rates, logging)

---

## 🔐 Security Features

✅ **Encrypted Credential Storage** - Passwords never stored in plain text  
✅ **Fernet Encryption** - Industry-standard symmetric encryption  
✅ **Secure Key Management** - Keys stored separately from credentials  
✅ **Auto-generated Keys** - First-time setup creates encryption key  

---

## 🎨 Visual Features

### Market Structure Chart Shows:
- **Candlestick price action** (4H timeframe)
- **Main Range** - High, Low, and Equilibrium (EQ)
- **Watch Pivot** - Minor structure level being monitored
- **Entry Setup** - Entry price, Stop Loss, Take Profit markers
- **Color-coded levels**:
  - 🔵 Blue: Main Range
  - 🟡 Yellow: Equilibrium (50%)
  - 🟣 Magenta: Watch Pivot
  - 🟢 Green: Entry & Take Profit
  - 🔴 Red: Stop Loss

---

## ⚠️ Important Notes

### Before Live Trading:
1. ✅ Test on **DEMO account** first
2. ✅ Verify **MT5 connection** in Settings
3. ✅ Start with **low risk** (0.5-1%)
4. ✅ Monitor **first trades** closely
5. ✅ Check **market conditions** are favorable

### Risk Management:
- Default: **1% risk per trade**
- Minimum R:R: **1:3**
- Stop Loss: **Structural + 20 pips buffer**
- Position size: **Auto-calculated**

---

## 🐛 Troubleshooting

### "MT5 Connection Failed"
- Check MT5 terminal is **running**
- Verify credentials in Settings
- Ensure **AlgoTrading** is enabled in MT5
- Click "Test Connection" to diagnose

### "No Data Available"
- Verify symbol (XAUUSD) exists in your broker
- Check Market Watch has symbol enabled
- Ensure sufficient historical data

### Dashboard Won't Load
- Check if port **8050** is available
- Try different browser
- Check firewall settings
- View logs: `smc_platform.log`

---

## 📊 Trading Logic Summary

### Phase 1: Main Structure (4H)
1. Detect **Main BOS** (body closes above/below pivot)
2. Establish **Main Range** (high, low)
3. Calculate **Equilibrium** (50% level)

### Phase 2: Pullback (1H)
1. Wait for **wick to touch EQ zone**
2. Identify **Watch Pivot** (recent 1H pivot)
3. Track **extreme** (lowest low / highest high)

### Phase 3: Minor MSS (1H)
1. Body closes **above/below Watch Pivot**
2. Lock extreme as **Minor Confirmed Level**

### Phase 4: Entry (15m)
1. Identify **Order Block** (last opposing candle)
2. Calculate entry at **OB open price**
3. Place **Limit Order** with SL & TP

---

## 🎯 Expected Behavior

When running properly:
- **Green indicator** in sidebar: "Connected • Live"
- **Balance updates** every 5 seconds
- **Chart updates** with new candles
- **State panel** shows current phase
- **Activity log** shows system events
- **Orders placed** automatically when setup confirmed

---

## 📞 Support

For issues:
1. Check `smc_platform.log` for errors
2. Verify MT5 connection in Settings → Test Connection
3. Ensure all dependencies installed: `pip install -r requirements.txt`
4. Test individual modules: `python data_feed.py`

---

## 🔄 Update Configuration

To change settings without restarting:
1. Go to **Settings** page
2. Modify parameters
3. Click **Save**
4. Changes apply on next data refresh (5 seconds)

---

**You're now ready to use the SMC Trading Platform Professional Edition!** 🚀

Start with Dashboard Only mode to familiarize yourself with the interface before enabling automated trading.
