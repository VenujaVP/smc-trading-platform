"""
Configuration Module for Advanced MTF SMC Trading Engine
Stores MT5 credentials, symbol settings, timeframes, and risk parameters.

NOTE: For security, configure MT5 credentials through the Settings page in the GUI.
      Credentials are encrypted and stored securely in config/credentials.enc
"""

import MetaTrader5 as mt5
from pathlib import Path

# ============================================================================
# MT5 CONNECTION SETTINGS (Loaded from secure storage)
# ============================================================================
MT5_ACCOUNT = None  # Loaded from encrypted storage
MT5_PASSWORD = None  # Loaded from encrypted storage
MT5_SERVER = None  # Loaded from encrypted storage

# Load credentials from settings if available
def load_credentials_from_settings():
    """Load credentials from secure settings storage."""
    try:
        from gui.utils.settings_manager import load_mt5_credentials
        creds = load_mt5_credentials()
        if creds:
            global MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER
            MT5_ACCOUNT = creds['account']
            MT5_PASSWORD = creds['password']
            MT5_SERVER = creds['server']
            return True
    except:
        pass
    return False

# ============================================================================
# MULTI-SYMBOL TRADING CONFIGURATION
# ============================================================================
# List of symbols to trade (can be modified via GUI or settings)
ACTIVE_SYMBOLS = ["XAUUSD"]  # Default: Gold only

# Symbol-specific configurations (loaded dynamically)
SYMBOL_CONFIGS = {}  # Will store per-symbol settings

# ============================================================================
# TIMEFRAME MAPPINGS (MT5 Constants) - Now Configurable per Symbol
# ============================================================================
# String to MT5 constant mapping
TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
    "W1": mt5.TIMEFRAME_W1,
    "MN1": mt5.TIMEFRAME_MN1
}

# Default timeframe configuration (can be changed per symbol)
DEFAULT_TIMEFRAMES = {
    "MAIN": "H4",      # Main Market Structure (default 4H, configurable)
    "MAIN_CONF": "H1",  # Main Confirmation (1H)
    "MINOR": "H1",      # Minor Market Structure Shift (default 1H, configurable)
    "ENTRY": "M15"      # Entry Timeframe (15m)
}

def get_timeframe_constant(tf_string):
    """Convert timeframe string to MT5 constant."""
    return TIMEFRAME_MAP.get(tf_string, mt5.TIMEFRAME_H4)

# ============================================================================
# PIVOT LOOKBACK PERIODS
# ============================================================================
MAIN_PIVOT_LOOKBACK = 5  # Candles to left and right for HTF pivots
MINOR_PIVOT_LOOKBACK = 2  # Candles to left and right for LTF pivots

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
RISK_PERCENT = 1.0  # Risk 1% of account equity per trade
MIN_RISK_REWARD = 3.0  # Minimum 1:3 R:R ratio
STOP_LOSS_BUFFER_PIPS = 20  # Additional buffer below/above structure

# ============================================================================
# DATA FETCH SETTINGS
# ============================================================================
CANDLES_TO_FETCH = 500  # Number of historical candles to fetch

# ============================================================================
# EXECUTION SETTINGS
# ============================================================================
SLIPPAGE_POINTS = 10  # Acceptable slippage in points
MAGIC_NUMBER = 234567  # Unique identifier for this bot's orders
ORDER_COMMENT = "SMC_MTF_Bot"

# ============================================================================
# LOOP TIMING (seconds)
# ============================================================================
SLEEP_INTERVAL = 60  # Check every 60 seconds (15m = 900s, but check more frequently)

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "smc_trading_bot.log"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_pip_value():
    """Calculate pip value based on symbol point."""
    if SYMBOL_INFO is None:
        return 0.0001  # Default for forex pairs
    
    point = SYMBOL_INFO.point
    # For XAUUSD and similar, 1 pip = 0.1 (10 points)
    if "XAU" in SYMBOL or "GOLD" in SYMBOL:
        return point * 10
    # For JPY pairs, 1 pip = 0.01
    elif "JPY" in SYMBOL:
        return 0.01
    # For most forex pairs, 1 pip = 0.0001
    else:
        return 0.0001

def pips_to_price(pips):
    """Convert pips to price difference."""
    return pips * get_pip_value()

def price_to_pips(price_diff):
    """Convert price difference to pips."""
    pip_value = get_pip_value()
    return price_diff / pip_value if pip_value > 0 else 0
