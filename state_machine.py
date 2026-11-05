"""
State Machine Module for Advanced MTF SMC Trading Engine
Manages the persistent state of market structure across loop iterations.
"""

import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS FOR STATE TRACKING
# ============================================================================

class MarketBias(Enum):
    """Overall market direction bias."""
    NEUTRAL = "NEUTRAL"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class Phase(Enum):
    """Current phase in the trading workflow."""
    WAITING_FOR_MAIN_BOS = "WAITING_FOR_MAIN_BOS"
    MAIN_RANGE_ESTABLISHED = "MAIN_RANGE_ESTABLISHED"
    WAITING_FOR_PULLBACK = "WAITING_FOR_PULLBACK"
    IN_DISCOUNT_ZONE = "IN_DISCOUNT_ZONE"
    IN_PREMIUM_ZONE = "IN_PREMIUM_ZONE"
    WAITING_FOR_MINOR_MSS = "WAITING_FOR_MINOR_MSS"
    MINOR_MSS_CONFIRMED = "MINOR_MSS_CONFIRMED"
    ORDER_PLACED = "ORDER_PLACED"


# ============================================================================
# DATA CLASSES FOR RANGE TRACKING
# ============================================================================

@dataclass
class Range:
    """Represents a price range with high and low."""
    high: Optional[float] = None
    low: Optional[float] = None
    confirmed: bool = False
    timestamp: Optional[datetime] = None
    
    def is_valid(self):
        """Check if range has both high and low defined."""
        return self.high is not None and self.low is not None
    
    def get_equilibrium(self):
        """Calculate 50% equilibrium of the range."""
        if not self.is_valid():
            return None
        return (self.high + self.low) / 2
    
    def get_size(self):
        """Calculate range size."""
        if not self.is_valid():
            return 0.0
        return abs(self.high - self.low)


@dataclass
class PivotTracker:
    """Tracks pivot points and their indices."""
    price: Optional[float] = None
    index: Optional[int] = None
    timestamp: Optional[datetime] = None
    confirmed: bool = False


# ============================================================================
# MAIN STATE MACHINE CLASS
# ============================================================================

class MarketState:
    """
    Persistent state machine that tracks multi-timeframe market structure.
    This object persists across loop iterations.
    """
    
    def __init__(self):
        # Core State
        self.bias = MarketBias.NEUTRAL
        self.phase = Phase.WAITING_FOR_MAIN_BOS
        
        # Main Structure (HTF)
        self.main_range = Range()
        self.main_pivot_high = PivotTracker()
        self.main_pivot_low = PivotTracker()
        self.main_bos_detected = False
        self.main_bos_timestamp = None
        
        # Minor Structure (LTF)
        self.minor_range = Range()
        self.watch_pivot = PivotTracker()  # The pivot we're watching for MSS
        self.tracked_extreme = None  # Tracked low (bullish) or high (bearish)
        self.minor_mss_confirmed = False
        self.minor_mss_timestamp = None
        
        # Entry Management
        self.entry_trigger_active = False
        self.order_block = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.position_open = False
        
        # Tracking
        self.last_update = None
        self.state_history = []
        
        logger.info("MarketState initialized")
    
    def reset_main_structure(self):
        """Reset main structure tracking."""
        self.main_range = Range()
        self.main_pivot_high = PivotTracker()
        self.main_pivot_low = PivotTracker()
        self.main_bos_detected = False
        self.phase = Phase.WAITING_FOR_MAIN_BOS
        logger.info("Main structure reset")
    
    def reset_minor_structure(self):
        """Reset minor structure tracking."""
        self.minor_range = Range()
        self.watch_pivot = PivotTracker()
        self.tracked_extreme = None
        self.minor_mss_confirmed = False
        logger.info("Minor structure reset")
    
    def reset_entry_tracking(self):
        """Reset entry-related tracking."""
        self.entry_trigger_active = False
        self.order_block = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        logger.info("Entry tracking reset")
    
    def set_bullish_bias(self, pivot_high_price, pivot_low_price, timestamp=None):
        """Establish bullish bias after main BOS."""
        self.bias = MarketBias.BULLISH
        self.main_bos_detected = True
        self.main_bos_timestamp = timestamp or datetime.now()
        
        # Set main range
        self.main_range.low = pivot_low_price
        self.main_range.confirmed = True
        self.main_pivot_low.price = pivot_low_price
        self.main_pivot_low.confirmed = True
        
        # Track unconfirmed high
        self.main_range.high = pivot_high_price
        self.main_pivot_high.price = pivot_high_price
        
        self.phase = Phase.MAIN_RANGE_ESTABLISHED
        
        logger.info(f"Bullish bias set | Low: {pivot_low_price} | High: {pivot_high_price}")
    
    def set_bearish_bias(self, pivot_high_price, pivot_low_price, timestamp=None):
        """Establish bearish bias after main BOS."""
        self.bias = MarketBias.BEARISH
        self.main_bos_detected = True
        self.main_bos_timestamp = timestamp or datetime.now()
        
        # Set main range
        self.main_range.high = pivot_high_price
        self.main_range.confirmed = True
        self.main_pivot_high.price = pivot_high_price
        self.main_pivot_high.confirmed = True
        
        # Track unconfirmed low
        self.main_range.low = pivot_low_price
        self.main_pivot_low.price = pivot_low_price
        
        self.phase = Phase.MAIN_RANGE_ESTABLISHED
        
        logger.info(f"Bearish bias set | High: {pivot_high_price} | Low: {pivot_low_price}")
    
    def update_unconfirmed_high(self, new_high):
        """Update the unconfirmed high of main range."""
        if new_high > (self.main_range.high or 0):
            self.main_range.high = new_high
            self.main_pivot_high.price = new_high
            logger.debug(f"Unconfirmed high updated: {new_high}")
    
    def update_unconfirmed_low(self, new_low):
        """Update the unconfirmed low of main range."""
        if self.main_range.low is None or new_low < self.main_range.low:
            self.main_range.low = new_low
            self.main_pivot_low.price = new_low
            logger.debug(f"Unconfirmed low updated: {new_low}")
    
    def confirm_main_high(self, timestamp=None):
        """Confirm the main range high (via 1H bearish BOS)."""
        self.main_pivot_high.confirmed = True
        self.main_pivot_high.timestamp = timestamp or datetime.now()
        logger.info(f"Main high confirmed at {self.main_range.high}")
    
    def confirm_main_low(self, timestamp=None):
        """Confirm the main range low (via 1H bullish BOS)."""
        self.main_pivot_low.confirmed = True
        self.main_pivot_low.timestamp = timestamp or datetime.now()
        logger.info(f"Main low confirmed at {self.main_range.low}")
    
    def enter_discount_zone(self):
        """Mark entry into discount zone."""
        self.phase = Phase.IN_DISCOUNT_ZONE
        logger.info("Entered discount zone - ready to track minor structure")
    
    def enter_premium_zone(self):
        """Mark entry into premium zone."""
        self.phase = Phase.IN_PREMIUM_ZONE
        logger.info("Entered premium zone - ready to track minor structure")
    
    def set_watch_pivot(self, pivot_price, pivot_index=None):
        """Set the pivot to watch for minor MSS."""
        self.watch_pivot.price = pivot_price
        self.watch_pivot.index = pivot_index
        self.watch_pivot.timestamp = datetime.now()
        self.phase = Phase.WAITING_FOR_MINOR_MSS
        logger.info(f"Watch pivot set at {pivot_price}")
    
    def update_tracked_extreme(self, extreme_price):
        """Update the tracked extreme (low for bullish, high for bearish)."""
        self.tracked_extreme = extreme_price
        logger.debug(f"Tracked extreme updated: {extreme_price}")
    
    def confirm_minor_mss(self, timestamp=None):
        """Confirm minor market structure shift."""
        self.minor_mss_confirmed = True
        self.minor_mss_timestamp = timestamp or datetime.now()
        self.phase = Phase.MINOR_MSS_CONFIRMED
        
        # Lock the tracked extreme as minor confirmed level
        if self.bias == MarketBias.BULLISH:
            self.minor_range.low = self.tracked_extreme
            self.minor_range.confirmed = True
            logger.info(f"Minor MSS confirmed | Minor Low locked: {self.tracked_extreme}")
        else:
            self.minor_range.high = self.tracked_extreme
            self.minor_range.confirmed = True
            logger.info(f"Minor MSS confirmed | Minor High locked: {self.tracked_extreme}")
    
    def set_entry_setup(self, order_block, entry_price, stop_loss, take_profit):
        """Store the calculated entry setup."""
        self.order_block = order_block
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_trigger_active = True
        self.phase = Phase.ORDER_PLACED
        
        logger.info(f"Entry setup prepared | Entry: {entry_price} | SL: {stop_loss} | TP: {take_profit}")
    
    def mark_position_opened(self):
        """Mark that a position has been opened."""
        self.position_open = True
        logger.info("Position opened - awaiting outcome")
    
    def reset_for_new_cycle(self):
        """Reset state for a new trading cycle."""
        self.reset_minor_structure()
        self.reset_entry_tracking()
        self.phase = Phase.WAITING_FOR_PULLBACK if self.main_bos_detected else Phase.WAITING_FOR_MAIN_BOS
        logger.info("State reset for new cycle")
    
    def get_status_summary(self) -> Dict:
        """Get a dictionary summary of current state."""
        return {
            'bias': self.bias.value,
            'phase': self.phase.value,
            'main_range_valid': self.main_range.is_valid(),
            'main_range_low': self.main_range.low,
            'main_range_high': self.main_range.high,
            'equilibrium': self.main_range.get_equilibrium(),
            'watch_pivot': self.watch_pivot.price,
            'tracked_extreme': self.tracked_extreme,
            'minor_mss_confirmed': self.minor_mss_confirmed,
            'entry_active': self.entry_trigger_active,
            'position_open': self.position_open,
            'last_update': self.last_update
        }
    
    def log_status(self):
        """Log current state to console."""
        status = self.get_status_summary()
        logger.info("=" * 60)
        logger.info("CURRENT STATE SUMMARY")
        logger.info("=" * 60)
        for key, value in status.items():
            logger.info(f"{key:.<30} {value}")
        logger.info("=" * 60)


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Testing State Machine...\n")
    
    # Initialize state
    state = MarketState()
    state.log_status()
    
    # Simulate bullish bias
    print("\n--- Setting Bullish Bias ---")
    state.set_bullish_bias(pivot_high_price=2050.0, pivot_low_price=2000.0)
    state.log_status()
    
    # Simulate entering discount zone
    print("\n--- Entering Discount Zone ---")
    state.enter_discount_zone()
    state.set_watch_pivot(pivot_price=2025.0)
    state.update_tracked_extreme(1998.0)
    state.log_status()
    
    # Simulate minor MSS
    print("\n--- Minor MSS Confirmed ---")
    state.confirm_minor_mss()
    state.log_status()
    
    print("\n✓ State Machine tests completed successfully!")
