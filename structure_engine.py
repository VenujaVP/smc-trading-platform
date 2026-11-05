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
# BREAKOUT DETECTION (BODY-BASED)
# ============================================================================

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
