"""
Structure Engine Module for Advanced MTF SMC Trading Engine
Pure logic module for calculating pivot points, detecting breakouts,
and identifying market structure shifts.
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PIVOT CALCULATION FUNCTIONS
# ============================================================================

def calculate_pivot_highs(df, lookback=5):
    """
    Calculate pivot highs using scipy's argrelextrema.
    
    Args:
        df: DataFrame with 'high' column
        lookback: Number of candles to left and right for comparison
    
    Returns:
        Series with True at pivot high indices, False otherwise
    """
    highs = df['high'].values
    pivot_indices = argrelextrema(highs, np.greater, order=lookback)[0]
    
    pivot_series = pd.Series(False, index=df.index)
    pivot_series.iloc[pivot_indices] = True
    
    return pivot_series


def calculate_pivot_lows(df, lookback=5):
    """
    Calculate pivot lows using scipy's argrelextrema.
    
    Args:
        df: DataFrame with 'low' column
        lookback: Number of candles to left and right for comparison
    
    Returns:
        Series with True at pivot low indices, False otherwise
    """
    lows = df['low'].values
    pivot_indices = argrelextrema(lows, np.less, order=lookback)[0]
    
    pivot_series = pd.Series(False, index=df.index)
    pivot_series.iloc[pivot_indices] = True
    
    return pivot_series


def get_most_recent_pivot(df, pivot_series, return_price=False, use_high=True):
    """
    Get the most recent pivot point from a pivot series.
    
    Args:
        df: Original DataFrame
        pivot_series: Boolean series indicating pivot locations
        return_price: If True, return the price; if False, return the index
        use_high: If True, use 'high' column; if False, use 'low' column
    
    Returns:
        Price or index of most recent pivot, or None if not found
    """
    pivot_indices = df[pivot_series].index
    
    if len(pivot_indices) == 0:
        return None
    
    most_recent_idx = pivot_indices[-1]
    
    if return_price:
        price_col = 'high' if use_high else 'low'
        return df.loc[most_recent_idx, price_col]
    else:
        return most_recent_idx


# ============================================================================
# BREAKOUT DETECTION (BODY-BASED) - UPDATED LOGIC
# ============================================================================

def detect_bullish_bos_first(df, lookback=5):
    """
    STEP 1: Detect Bullish Break of Structure FIRST (before finding pivots).
    
    Logic:
    1. Calculate pivot highs using lookback period
    2. Get the most recent valid pivot high
    3. Check if latest candle BODY (close) breaks above that pivot high
    
    Args:
        df: DataFrame with OHLC data
        lookback: Pivot lookback period
    
    Returns:
        (bos_detected: bool, pivot_high_price: float, pivot_low_price: float)
    """
    if df is None or df.empty or len(df) < lookback * 2 + 1:
        return False, None, None
    
    # Calculate pivot highs and lows
    pivot_highs = calculate_pivot_highs(df, lookback=lookback)
    pivot_lows = calculate_pivot_lows(df, lookback=lookback)
    
    # Get most recent pivot high (resistance to break)
    recent_pivot_high = get_most_recent_pivot(df, pivot_highs, return_price=True, use_high=True)
    
    if recent_pivot_high is None:
        return False, None, None
    
    # Check if latest candle BODY closes ABOVE the pivot high
    latest_close = df.iloc[-1]['close']
    
    if latest_close > recent_pivot_high:
        # BOS detected! Now find the pivot low BEFORE this breakout
        # Get the pivot low that was established before the most recent pivot high
        pivot_low_price = get_pivot_low_before_high(df, pivot_highs, pivot_lows)
        
        logger.info(f"🚀 BULLISH BOS DETECTED | Body closed above {recent_pivot_high:.2f}")
        return True, recent_pivot_high, pivot_low_price
    
    return False, None, None


def detect_bearish_bos_first(df, lookback=5):
    """
    STEP 1: Detect Bearish Break of Structure FIRST (before finding pivots).
    
    Logic:
    1. Calculate pivot lows using lookback period
    2. Get the most recent valid pivot low
    3. Check if latest candle BODY (close) breaks below that pivot low
    
    Args:
        df: DataFrame with OHLC data
        lookback: Pivot lookback period
    
    Returns:
        (bos_detected: bool, pivot_low_price: float, pivot_high_price: float)
    """
    if df is None or df.empty or len(df) < lookback * 2 + 1:
        return False, None, None
    
    # Calculate pivot highs and lows
    pivot_highs = calculate_pivot_highs(df, lookback=lookback)
    pivot_lows = calculate_pivot_lows(df, lookback=lookback)
    
    # Get most recent pivot low (support to break)
    recent_pivot_low = get_most_recent_pivot(df, pivot_lows, return_price=True, use_high=False)
    
    if recent_pivot_low is None:
        return False, None, None
    
    # Check if latest candle BODY closes BELOW the pivot low
    latest_close = df.iloc[-1]['close']
    
    if latest_close < recent_pivot_low:
        # BOS detected! Now find the pivot high BEFORE this breakout
        pivot_high_price = get_pivot_high_before_low(df, pivot_highs, pivot_lows)
        
        logger.info(f"🔻 BEARISH BOS DETECTED | Body closed below {recent_pivot_low:.2f}")
        return True, recent_pivot_low, pivot_high_price
    
    return False, None, None


def get_pivot_low_before_high(df, pivot_highs, pivot_lows):
    """
    Find the pivot low that was established BEFORE the most recent pivot high.
    This becomes the Main Range Low for bullish bias.
    
    Args:
        df: DataFrame with OHLC
        pivot_highs: Boolean series of pivot high locations
        pivot_lows: Boolean series of pivot low locations
    
    Returns:
        Price of the pivot low before the breakout
    """
    try:
        # Get index of most recent pivot high
        high_indices = df[pivot_highs].index.tolist()
        if not high_indices:
            return None
        
        last_high_idx = high_indices[-1]
        
        # Get all pivot lows before this high
        low_indices = df[pivot_lows].index.tolist()
        lows_before_high = [idx for idx in low_indices if idx < last_high_idx]
        
        if not lows_before_high:
            # If no pivot low before high, use absolute lowest low in recent data
            recent_data = df.iloc[-50:]  # Last 50 candles
            return recent_data['low'].min()
        
        # Get the most recent pivot low before the high
        last_low_idx = lows_before_high[-1]
        return df.loc[last_low_idx, 'low']
    
    except Exception as e:
        logger.error(f"Error finding pivot low before high: {e}")
        # Fallback: return lowest low in recent data
        return df.iloc[-50:]['low'].min()


def get_pivot_high_before_low(df, pivot_highs, pivot_lows):
    """
    Find the pivot high that was established BEFORE the most recent pivot low.
    This becomes the Main Range High for bearish bias.
    
    Args:
        df: DataFrame with OHLC
        pivot_highs: Boolean series of pivot high locations
        pivot_lows: Boolean series of pivot low locations
    
    Returns:
        Price of the pivot high before the breakout
    """
    try:
        # Get index of most recent pivot low
        low_indices = df[pivot_lows].index.tolist()
        if not low_indices:
            return None
        
        last_low_idx = low_indices[-1]
        
        # Get all pivot highs before this low
        high_indices = df[pivot_highs].index.tolist()
        highs_before_low = [idx for idx in high_indices if idx < last_low_idx]
        
        if not highs_before_low:
            # If no pivot high before low, use absolute highest high in recent data
            recent_data = df.iloc[-50:]
            return recent_data['high'].max()
        
        # Get the most recent pivot high before the low
        last_high_idx = highs_before_low[-1]
        return df.loc[last_high_idx, 'high']
    
    except Exception as e:
        logger.error(f"Error finding pivot high before low: {e}")
        # Fallback: return highest high in recent data
        return df.iloc[-50:]['high'].max()


def detect_bullish_body_breakout(df, resistance_level):
    """
    Detect if the most recent candle's CLOSE (body) breaks above resistance.
    
    Args:
        df: DataFrame with 'close' column
        resistance_level: Price level to break
    
    Returns:
        True if breakout detected, False otherwise
    """
    if df.empty or resistance_level is None:
        return False
    
    latest_close = df.iloc[-1]['close']
    return latest_close > resistance_level


def detect_bearish_body_breakout(df, support_level):
    """
    Detect if the most recent candle's CLOSE (body) breaks below support.
    
    Args:
        df: DataFrame with 'close' column
        support_level: Price level to break
    
    Returns:
        True if breakout detected, False otherwise
    """
    if df.empty or support_level is None:
        return False
    
    latest_close = df.iloc[-1]['close']
    return latest_close < support_level


# ============================================================================
# ZONE DETECTION (WICK-BASED)
# ============================================================================

def detect_wick_in_discount_zone(df, eq_level):
    """
    Check if the most recent candle's LOW (wick) touches or goes below EQ.
    
    Args:
        df: DataFrame with 'low' column
        eq_level: Equilibrium level (50% of range)
    
    Returns:
        True if wick enters discount zone, False otherwise
    """
    if df.empty or eq_level is None:
        return False
    
    latest_low = df.iloc[-1]['low']
    return latest_low <= eq_level


def detect_wick_in_premium_zone(df, eq_level):
    """
    Check if the most recent candle's HIGH (wick) touches or goes above EQ.
    
    Args:
        df: DataFrame with 'low' column
        eq_level: Equilibrium level (50% of range)
    
    Returns:
        True if wick enters premium zone, False otherwise
    """
    if df.empty or eq_level is None:
        return False
    
    latest_high = df.iloc[-1]['high']
    return latest_high >= eq_level


# ============================================================================
# EXTREME TRACKING
# ============================================================================

def get_lowest_low_since_index(df, start_idx):
    """
    Get the absolute lowest LOW since a specific index.
    
    Args:
        df: DataFrame with 'low' column
        start_idx: Starting index
    
    Returns:
        Lowest low value
    """
    if start_idx >= len(df):
        return None
    
    subset = df.iloc[start_idx:]
    return subset['low'].min()


def get_highest_high_since_index(df, start_idx):
    """
    Get the absolute highest HIGH since a specific index.
    
    Args:
        df: DataFrame with 'high' column
        start_idx: Starting index
    
    Returns:
        Highest high value
    """
    if start_idx >= len(df):
        return None
    
    subset = df.iloc[start_idx:]
    return subset['high'].max()


# ============================================================================
# ORDER BLOCK DETECTION
# ============================================================================

def find_order_block(df, breakout_idx, direction='bullish'):
    """
    Find the Order Block that caused the breakout.
    
    For a bullish breakout: Find the last bearish candle before the push.
    For a bearish breakout: Find the last bullish candle before the push.
    
    Args:
        df: DataFrame with OHLC data
        breakout_idx: Index where the breakout occurred
        direction: 'bullish' or 'bearish'
    
    Returns:
        Dictionary with 'high', 'low', 'open', 'close' of the OB candle,
        or None if not found
    """
    if breakout_idx < 1 or breakout_idx >= len(df):
        return None
    
    # Look backwards from the breakout candle
    for i in range(breakout_idx - 1, max(0, breakout_idx - 10), -1):
        candle = df.iloc[i]
        
        if direction == 'bullish':
            # Find last bearish candle (close < open)
            if candle['close'] < candle['open']:
                return {
                    'high': candle['high'],
                    'low': candle['low'],
                    'open': candle['open'],
                    'close': candle['close'],
                    'index': i
                }
        else:  # bearish
            # Find last bullish candle (close > open)
            if candle['close'] > candle['open']:
                return {
                    'high': candle['high'],
                    'low': candle['low'],
                    'open': candle['open'],
                    'close': candle['close'],
                    'index': i
                }
    
    return None


def calculate_ob_entry_price(order_block, direction='bullish'):
    """
    Calculate the entry price from an Order Block.
    
    For bullish: Use the OPEN of the bearish OB candle
    For bearish: Use the OPEN of the bullish OB candle
    
    Args:
        order_block: Dictionary from find_order_block()
        direction: 'bullish' or 'bearish'
    
    Returns:
        Entry price as float
    """
    if order_block is None:
        return None
    
    return order_block['open']


def calculate_fvg_entry_price(order_block, direction='bullish'):
    """
    Calculate entry at 50% of the Fair Value Gap.
    
    Args:
        order_block: Dictionary from find_order_block()
        direction: 'bullish' or 'bearish'
    
    Returns:
        Entry price at 50% of OB range
    """
    if order_block is None:
        return None
    
    return (order_block['high'] + order_block['low']) / 2


# ============================================================================
# EQUILIBRIUM CALCULATION
# ============================================================================

def calculate_equilibrium(range_high, range_low):
    """
    Calculate the 50% equilibrium level between high and low.
    
    Args:
        range_high: High of the range
        range_low: Low of the range
    
    Returns:
        Equilibrium price level
    """
    if range_high is None or range_low is None:
        return None
    
    return (range_high + range_low) / 2


# ============================================================================
# STRUCTURE VALIDATION
# ============================================================================

def is_valid_range(range_high, range_low, min_pips=10):
    """
    Validate if a range is significant enough to trade.
    
    Args:
        range_high: High of the range
        range_low: Low of the range
        min_pips: Minimum range size in pips
    
    Returns:
        True if valid, False otherwise
    """
    if range_high is None or range_low is None:
        return False
    
    from config import price_to_pips
    range_pips = price_to_pips(abs(range_high - range_low))
    
    return range_pips >= min_pips


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    sample_data = {
        'time': pd.date_range('2024-01-01', periods=100, freq='H'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 100)
    }
    df = pd.DataFrame(sample_data)
    
    # Ensure high is actually highest and low is lowest
    df['high'] = df[['open', 'close']].max(axis=1) + abs(np.random.randn(100) * 0.5)
    df['low'] = df[['open', 'close']].min(axis=1) - abs(np.random.randn(100) * 0.5)
    
    print("Testing Structure Engine...")
    
    # Test pivot calculation
    pivot_highs = calculate_pivot_highs(df, lookback=5)
    pivot_lows = calculate_pivot_lows(df, lookback=5)
    
    print(f"✓ Pivot Highs detected: {pivot_highs.sum()}")
    print(f"✓ Pivot Lows detected: {pivot_lows.sum()}")
    
    # Test most recent pivot
    recent_ph = get_most_recent_pivot(df, pivot_highs, return_price=True, use_high=True)
    print(f"✓ Most recent Pivot High: {recent_ph}")
    
    # Test equilibrium
    eq = calculate_equilibrium(df['high'].max(), df['low'].min())
    print(f"✓ Equilibrium: {eq}")
    
    print("\nStructure Engine tests completed successfully!")
