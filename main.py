"""
Main Execution Loop for Advanced MTF SMC Trading Engine
Orchestrates the entire trading workflow.
"""

import time
import logging
from datetime import datetime
import sys

import config
from data_feed import MT5DataFeed
from state_machine import MarketState, MarketBias, Phase
from structure_engine import (
    calculate_pivot_highs, calculate_pivot_lows, get_most_recent_pivot,
    detect_bullish_body_breakout, detect_bearish_body_breakout,
    detect_wick_in_discount_zone, detect_wick_in_premium_zone,
    get_lowest_low_since_index, get_highest_high_since_index,
    find_order_block, calculate_ob_entry_price,
    calculate_equilibrium
)
from execution import OrderExecutor


# ============================================================================
# LOGGING SETUP
# ============================================================================
def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)


# ============================================================================
# CORE LOGIC FUNCTIONS
# ============================================================================

def check_main_bos(state, htf_df):
    """
    Phase 1: Check for Main Break of Structure on HTF (4H).
    """
    if state.phase != Phase.WAITING_FOR_MAIN_BOS:
        return
    
    logger.debug("Checking for Main BOS...")
    
    # Calculate pivots
    pivot_highs = calculate_pivot_highs(htf_df, lookback=config.MAIN_PIVOT_LOOKBACK)
    pivot_lows = calculate_pivot_lows(htf_df, lookback=config.MAIN_PIVOT_LOOKBACK)
    
    # Get most recent pivots
    recent_ph = get_most_recent_pivot(htf_df, pivot_highs, return_price=True, use_high=True)
    recent_pl = get_most_recent_pivot(htf_df, pivot_lows, return_price=True, use_high=False)
    
    if recent_ph is None or recent_pl is None:
        logger.debug("Insufficient pivot data")
        return
    
    # Check for bullish BOS (body closes above recent pivot high)
    if detect_bullish_body_breakout(htf_df, recent_ph):
        logger.info(f"🚀 BULLISH MAIN BOS DETECTED | Broke: {recent_ph}")
        state.set_bullish_bias(pivot_high_price=recent_ph, pivot_low_price=recent_pl)
        return
    
    # Check for bearish BOS (body closes below recent pivot low)
    if detect_bearish_body_breakout(htf_df, recent_pl):
        logger.info(f"🔻 BEARISH MAIN BOS DETECTED | Broke: {recent_pl}")
        state.set_bearish_bias(pivot_high_price=recent_ph, pivot_low_price=recent_pl)
        return


def update_main_range(state, htf_df, conf_df):
    """
    Phase 1 Continued: Update and confirm main range.
    """
    if state.phase != Phase.MAIN_RANGE_ESTABLISHED:
        return
    
    # Update unconfirmed extremes
    current_high = htf_df['high'].max()
    current_low = htf_df['low'].min()
    
    if state.bias == MarketBias.BULLISH:
        state.update_unconfirmed_high(current_high)
        
        # Check if 1H confirms the high with bearish BOS
        conf_pivot_highs = calculate_pivot_highs(conf_df, lookback=config.MINOR_PIVOT_LOOKBACK)
        recent_conf_ph = get_most_recent_pivot(conf_df, conf_pivot_highs, return_price=True, use_high=True)
        
        if recent_conf_ph and detect_bearish_body_breakout(conf_df, recent_conf_ph):
            state.confirm_main_high()
    
    elif state.bias == MarketBias.BEARISH:
        state.update_unconfirmed_low(current_low)
        
        # Check if 1H confirms the low with bullish BOS
        conf_pivot_lows = calculate_pivot_lows(conf_df, lookback=config.MINOR_PIVOT_LOOKBACK)
        recent_conf_pl = get_most_recent_pivot(conf_df, conf_pivot_lows, return_price=True, use_high=False)
        
        if recent_conf_pl and detect_bullish_body_breakout(conf_df, recent_conf_pl):
            state.confirm_main_low()
    
    # Move to pullback waiting phase
    state.phase = Phase.WAITING_FOR_PULLBACK


def check_pullback_to_eq(state, minor_df):
    """
    Phase 2: Check if price has pulled back to equilibrium zone.
    """
    if state.phase != Phase.WAITING_FOR_PULLBACK:
        return
    
    eq_level = state.main_range.get_equilibrium()
    if eq_level is None:
        return
    
    if state.bias == MarketBias.BULLISH:
        # Check if wick touches discount zone (below EQ)
        if detect_wick_in_discount_zone(minor_df, eq_level):
            logger.info(f"📉 Pullback to DISCOUNT ZONE | EQ: {eq_level}")
            state.enter_discount_zone()
    
    elif state.bias == MarketBias.BEARISH:
        # Check if wick touches premium zone (above EQ)
        if detect_wick_in_premium_zone(minor_df, eq_level):
            logger.info(f"📈 Pullback to PREMIUM ZONE | EQ: {eq_level}")
            state.enter_premium_zone()


def track_minor_structure(state, minor_df):
    """
    Phase 2 Continued: Track minor pivot and extreme.
    """
    if state.phase not in [Phase.IN_DISCOUNT_ZONE, Phase.IN_PREMIUM_ZONE]:
        return
    
    if state.bias == MarketBias.BULLISH and state.phase == Phase.IN_DISCOUNT_ZONE:
        # Find most recent 1H pivot high (Watch High)
        pivot_highs = calculate_pivot_highs(minor_df, lookback=config.MINOR_PIVOT_LOOKBACK)
        watch_high = get_most_recent_pivot(minor_df, pivot_highs, return_price=True, use_high=True)
        
        if watch_high:
            state.set_watch_pivot(watch_high)
            
            # Track the extreme low in the zone
            zone_entry_idx = len(minor_df) - 50  # Approximate zone entry
            extreme_low = get_lowest_low_since_index(minor_df, zone_entry_idx)
            if extreme_low:
                state.update_tracked_extreme(extreme_low)
    
    elif state.bias == MarketBias.BEARISH and state.phase == Phase.IN_PREMIUM_ZONE:
        # Find most recent 1H pivot low (Watch Low)
        pivot_lows = calculate_pivot_lows(minor_df, lookback=config.MINOR_PIVOT_LOOKBACK)
        watch_low = get_most_recent_pivot(minor_df, pivot_lows, return_price=True, use_high=False)
        
        if watch_low:
            state.set_watch_pivot(watch_low)
            
            # Track the extreme high in the zone
            zone_entry_idx = len(minor_df) - 50
            extreme_high = get_highest_high_since_index(minor_df, zone_entry_idx)
            if extreme_high:
                state.update_tracked_extreme(extreme_high)


def check_minor_mss(state, minor_df):
    """
    Phase 3: Check for Minor Market Structure Shift.
    """
    if state.phase != Phase.WAITING_FOR_MINOR_MSS:
        return
    
    if state.watch_pivot.price is None:
        return
    
    if state.bias == MarketBias.BULLISH:
        # Check if body breaks above Watch High
        if detect_bullish_body_breakout(minor_df, state.watch_pivot.price):
            logger.info(f"✅ MINOR MSS CONFIRMED (Bullish) | Broke: {state.watch_pivot.price}")
            state.confirm_minor_mss()
    
    elif state.bias == MarketBias.BEARISH:
        # Check if body breaks below Watch Low
        if detect_bearish_body_breakout(minor_df, state.watch_pivot.price):
            logger.info(f"✅ MINOR MSS CONFIRMED (Bearish) | Broke: {state.watch_pivot.price}")
            state.confirm_minor_mss()


def prepare_entry_setup(state, entry_df, executor, account_info):
    """
    Phase 4: Prepare the entry setup using Order Block logic.
    """
    if state.phase != Phase.MINOR_MSS_CONFIRMED:
        return False
    
    if state.entry_trigger_active:
        return False
    
    logger.info("Preparing entry setup...")
    
    # Find the Order Block
    direction = 'bullish' if state.bias == MarketBias.BULLISH else 'bearish'
    order_block = find_order_block(entry_df, breakout_idx=len(entry_df)-1, direction=direction)
    
    if order_block is None:
        logger.warning("Could not identify Order Block - skipping trade")
        state.reset_for_new_cycle()
        return False
    
    # Calculate entry price (use OB open)
    entry_price = calculate_ob_entry_price(order_block, direction=direction)
    
    # Calculate stop loss
    if state.bias == MarketBias.BULLISH:
        stop_loss = state.tracked_extreme - config.pips_to_price(config.STOP_LOSS_BUFFER_PIPS)
        take_profit = state.main_range.high  # Target main unconfirmed high
    else:
        stop_loss = state.tracked_extreme + config.pips_to_price(config.STOP_LOSS_BUFFER_PIPS)
        take_profit = state.main_range.low  # Target main unconfirmed low
    
    # Validate setup
    is_valid, reason = executor.validate_trade_setup(
        entry_price, stop_loss, take_profit, account_info['balance']
    )
    
    if not is_valid:
        logger.warning(f"Trade setup invalid: {reason}")
        state.reset_for_new_cycle()
        return False
    
    # Calculate position size
    lot_size = executor.calculate_position_size(
        account_info['balance'], entry_price, stop_loss
    )
    
    # Store setup in state
    state.set_entry_setup(order_block, entry_price, stop_loss, take_profit)
    
    # Place the order
    if state.bias == MarketBias.BULLISH:
        result = executor.place_buy_limit(entry_price, stop_loss, take_profit, lot_size)
    else:
        result = executor.place_sell_limit(entry_price, stop_loss, take_profit, lot_size)
    
    if result:
        state.mark_position_opened()
        logger.info("🎯 TRADE PLACED SUCCESSFULLY")
        return True
    else:
        logger.error("Failed to place order")
        state.reset_for_new_cycle()
        return False


# ============================================================================
# MAIN EXECUTION LOOP
# ============================================================================

def main():
    """Main trading loop."""
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("ADVANCED MTF SMC TRADING ENGINE - STARTING")
    logger.info("=" * 80)
    
    # Initialize components
    feed = MT5DataFeed()
    state = MarketState()
    executor = OrderExecutor()
    
    # Connect to MT5
    if not feed.initialize():
        logger.error("Failed to initialize MT5 - exiting")
        return
    
    try:
        iteration = 0
        
        while True:
            iteration += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"ITERATION {iteration} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*80}\n")
            
            # Fetch all timeframe data
            data = feed.fetch_all_timeframes()
            if data is None:
                logger.error("Failed to fetch data - retrying in next iteration")
                time.sleep(config.SLEEP_INTERVAL)
                continue
            
            htf_df = data['HTF']
            conf_df = data['MAIN_CONF']
            minor_df = data['MINOR']
            entry_df = data['ENTRY']
            
            # Get account info
            account_info = feed.get_account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                time.sleep(config.SLEEP_INTERVAL)
                continue
            
            logger.info(f"Account Balance: ${account_info['balance']:.2f} | Equity: ${account_info['equity']:.2f}")
            
            # Check if we already have a position
            open_positions = executor.get_open_positions()
            if len(open_positions) > 0:
                logger.info(f"Active position detected - monitoring...")
                state.log_status()
                time.sleep(config.SLEEP_INTERVAL)
                continue
            
            # If we had a position that closed, reset for new cycle
            if state.position_open and len(open_positions) == 0:
                logger.info("Position closed - resetting for new cycle")
                state.reset_for_new_cycle()
            
            # Execute the pipeline
            state.last_update = datetime.now()
            
            # Phase 1: Main Structure
            check_main_bos(state, htf_df)
            update_main_range(state, htf_df, conf_df)
            
            # Phase 2: Pullback
            check_pullback_to_eq(state, minor_df)
            track_minor_structure(state, minor_df)
            
            # Phase 3: Minor MSS
            check_minor_mss(state, minor_df)
            
            # Phase 4: Entry
            prepare_entry_setup(state, entry_df, executor, account_info)
            
            # Log current state
            state.log_status()
            
            # Sleep until next iteration
            logger.info(f"\nSleeping for {config.SLEEP_INTERVAL} seconds...\n")
            time.sleep(config.SLEEP_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested by user")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    
    finally:
        # Cleanup
        logger.info("Shutting down...")
        feed.shutdown()
        logger.info("=" * 80)
        logger.info("ADVANCED MTF SMC TRADING ENGINE - STOPPED")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()
