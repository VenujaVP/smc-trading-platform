"""
Multi-Symbol Main Execution Loop
Runs SMC trading strategy on multiple symbols simultaneously.
Each symbol has independent state and configuration.
"""

import time
import logging
from datetime import datetime
import sys

import config
from data_feed import MT5DataFeed
from state_machine import MarketState, MarketBias, Phase
from symbol_manager import get_symbol_manager, SymbolConfig
from structure_engine import (
    detect_bullish_bos_first, detect_bearish_bos_first,
    calculate_pivot_highs, calculate_pivot_lows, get_most_recent_pivot,
    detect_bullish_body_breakout, detect_bearish_body_breakout,
    detect_wick_in_discount_zone, detect_wick_in_premium_zone,
    get_lowest_low_since_index, get_highest_high_since_index,
    find_order_block, calculate_ob_entry_price
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
# CORE LOGIC FUNCTIONS (Symbol-Specific)
# ============================================================================

def check_main_bos_for_symbol(state, htf_df, symbol_config: SymbolConfig):
    """
    Phase 1: Check for Main Break of Structure.
    Uses symbol-specific lookback configuration.
    """
    if state.phase != Phase.WAITING_FOR_MAIN_BOS:
        return
    
    # Check for BULLISH BOS first
    bullish_bos, pivot_high, pivot_low = detect_bullish_bos_first(
        htf_df, 
        lookback=symbol_config.main_pivot_lookback
    )
    
    if bullish_bos and pivot_high and pivot_low:
        logger.info(f"[{symbol_config.symbol}] 🚀 BULLISH BOS | High: {pivot_high:.2f}, Low: {pivot_low:.2f}")
        state.set_bullish_bias(pivot_high_price=pivot_high, pivot_low_price=pivot_low)
        return
    
    # Check for BEARISH BOS
    bearish_bos, pivot_low, pivot_high = detect_bearish_bos_first(
        htf_df,
        lookback=symbol_config.main_pivot_lookback
    )
    
    if bearish_bos and pivot_low and pivot_high:
        logger.info(f"[{symbol_config.symbol}] 🔻 BEARISH BOS | Low: {pivot_low:.2f}, High: {pivot_high:.2f}")
        state.set_bearish_bias(pivot_high_price=pivot_high, pivot_low_price=pivot_low)
        return


def update_main_range_for_symbol(state, htf_df, conf_df, symbol_config: SymbolConfig):
    """
    Phase 1 Continued: Update and confirm main range.
    
    CRITICAL: Track the ACTUAL highest/lowest reached AFTER BOS, not the broken pivot.
    """
    if state.phase != Phase.MAIN_RANGE_ESTABLISHED:
        return
    
    if state.bias == MarketBias.BULLISH:
        # Find highest HIGH reached since BOS (dynamic tracking)
        # Use recent window to track the move after BOS
        recent_window = htf_df.iloc[-20:]  # Last 20 candles
        current_highest = recent_window['high'].max()
        
        # Update Main Range High dynamically (NOT locked)
        if current_highest > state.main_range.high:
            state.update_unconfirmed_high(current_highest)
            logger.debug(f"Main Range High updated: {current_highest:.2f}")
        
        # Confirm Main Range High when 1H shows bearish BOS
        conf_pivot_highs = calculate_pivot_highs(conf_df, lookback=symbol_config.minor_pivot_lookback)
        recent_conf_ph = get_most_recent_pivot(conf_df, conf_pivot_highs, return_price=True, use_high=True)
        
        if recent_conf_ph and detect_bearish_body_breakout(conf_df, recent_conf_ph):
            state.confirm_main_high()
    
    elif state.bias == MarketBias.BEARISH:
        # Find lowest LOW reached since BOS (dynamic tracking)
        recent_window = htf_df.iloc[-20:]
        current_lowest = recent_window['low'].min()
        
        # Update Main Range Low dynamically (NOT locked)
        if current_lowest < state.main_range.low:
            state.update_unconfirmed_low(current_lowest)
            logger.debug(f"Main Range Low updated: {current_lowest:.2f}")
        
        # Confirm Main Range Low when 1H shows bullish BOS
        conf_pivot_lows = calculate_pivot_lows(conf_df, lookback=symbol_config.minor_pivot_lookback)
        recent_conf_pl = get_most_recent_pivot(conf_df, conf_pivot_lows, return_price=True, use_high=False)
        
        if recent_conf_pl and detect_bullish_body_breakout(conf_df, recent_conf_pl):
            state.confirm_main_low()
    
    state.phase = Phase.WAITING_FOR_PULLBACK


def check_pullback_to_eq_for_symbol(state, minor_df, symbol_config: SymbolConfig):
    """Phase 2: Check if price has pulled back to equilibrium zone."""
    if state.phase != Phase.WAITING_FOR_PULLBACK:
        return
    
    eq_level = state.main_range.get_equilibrium()
    if eq_level is None:
        return
    
    if state.bias == MarketBias.BULLISH:
        if detect_wick_in_discount_zone(minor_df, eq_level):
            logger.info(f"[{symbol_config.symbol}] 📉 Pullback to DISCOUNT ZONE | EQ: {eq_level:.2f}")
            state.enter_discount_zone()
    
    elif state.bias == MarketBias.BEARISH:
        if detect_wick_in_premium_zone(minor_df, eq_level):
            logger.info(f"[{symbol_config.symbol}] 📈 Pullback to PREMIUM ZONE | EQ: {eq_level:.2f}")
            state.enter_premium_zone()


def track_minor_structure_for_symbol(state, minor_df, symbol_config: SymbolConfig):
    """Phase 2 Continued: Track minor pivot and extreme."""
    if state.phase not in [Phase.IN_DISCOUNT_ZONE, Phase.IN_PREMIUM_ZONE]:
        return
    
    if state.bias == MarketBias.BULLISH and state.phase == Phase.IN_DISCOUNT_ZONE:
        pivot_highs = calculate_pivot_highs(minor_df, lookback=symbol_config.minor_pivot_lookback)
        watch_high = get_most_recent_pivot(minor_df, pivot_highs, return_price=True, use_high=True)
        
        if watch_high:
            state.set_watch_pivot(watch_high)
            zone_entry_idx = len(minor_df) - 50
            extreme_low = get_lowest_low_since_index(minor_df, zone_entry_idx)
            if extreme_low:
                state.update_tracked_extreme(extreme_low)
    
    elif state.bias == MarketBias.BEARISH and state.phase == Phase.IN_PREMIUM_ZONE:
        pivot_lows = calculate_pivot_lows(minor_df, lookback=symbol_config.minor_pivot_lookback)
        watch_low = get_most_recent_pivot(minor_df, pivot_lows, return_price=True, use_high=False)
        
        if watch_low:
            state.set_watch_pivot(watch_low)
            zone_entry_idx = len(minor_df) - 50
            extreme_high = get_highest_high_since_index(minor_df, zone_entry_idx)
            if extreme_high:
                state.update_tracked_extreme(extreme_high)


def check_minor_mss_for_symbol(state, minor_df, symbol_config: SymbolConfig):
    """Phase 3: Check for Minor Market Structure Shift."""
    if state.phase != Phase.WAITING_FOR_MINOR_MSS:
        return
    
    if state.watch_pivot.price is None:
        return
    
    if state.bias == MarketBias.BULLISH:
        if detect_bullish_body_breakout(minor_df, state.watch_pivot.price):
            logger.info(f"[{symbol_config.symbol}] ✅ MINOR MSS (Bullish) | Broke: {state.watch_pivot.price:.2f}")
            state.confirm_minor_mss()
    
    elif state.bias == MarketBias.BEARISH:
        if detect_bearish_body_breakout(minor_df, state.watch_pivot.price):
            logger.info(f"[{symbol_config.symbol}] ✅ MINOR MSS (Bearish) | Broke: {state.watch_pivot.price:.2f}")
            state.confirm_minor_mss()


def prepare_entry_for_symbol(state, entry_df, executor, account_info, symbol_config: SymbolConfig):
    """Phase 4: Prepare the entry setup using Order Block logic."""
    if state.phase != Phase.MINOR_MSS_CONFIRMED:
        return False
    
    if state.entry_trigger_active:
        return False
    
    logger.info(f"[{symbol_config.symbol}] Preparing entry setup...")
    
    direction = 'bullish' if state.bias == MarketBias.BULLISH else 'bearish'
    order_block = find_order_block(entry_df, breakout_idx=len(entry_df)-1, direction=direction)
    
    if order_block is None:
        logger.warning(f"[{symbol_config.symbol}] Could not identify Order Block - skipping")
        state.reset_for_new_cycle()
        return False
    
    entry_price = calculate_ob_entry_price(order_block, direction=direction)
    
    if state.bias == MarketBias.BULLISH:
        stop_loss = state.tracked_extreme - config.pips_to_price(symbol_config.stop_loss_buffer_pips)
        take_profit = state.main_range.high
    else:
        stop_loss = state.tracked_extreme + config.pips_to_price(symbol_config.stop_loss_buffer_pips)
        take_profit = state.main_range.low
    
    is_valid, reason = executor.validate_trade_setup(
        entry_price, stop_loss, take_profit, account_info['balance']
    )
    
    if not is_valid:
        logger.warning(f"[{symbol_config.symbol}] Trade invalid: {reason}")
        state.reset_for_new_cycle()
        return False
    
    # Check R:R against symbol-specific minimum
    rr = executor.calculate_risk_reward_ratio(entry_price, stop_loss, take_profit)
    if rr < symbol_config.min_risk_reward:
        logger.warning(f"[{symbol_config.symbol}] R:R {rr:.2f} below minimum {symbol_config.min_risk_reward}")
        state.reset_for_new_cycle()
        return False
    
    lot_size = executor.calculate_position_size(
        account_info['balance'], entry_price, stop_loss, risk_percent=symbol_config.risk_percent
    )
    
    state.set_entry_setup(order_block, entry_price, stop_loss, take_profit)
    
    if state.bias == MarketBias.BULLISH:
        result = executor.place_buy_limit(entry_price, stop_loss, take_profit, lot_size, 
                                          comment=f"SMC_{symbol_config.symbol}")
    else:
        result = executor.place_sell_limit(entry_price, stop_loss, take_profit, lot_size,
                                           comment=f"SMC_{symbol_config.symbol}")
    
    if result:
        state.mark_position_opened()
        logger.info(f"[{symbol_config.symbol}] 🎯 TRADE PLACED")
        return True
    else:
        logger.error(f"[{symbol_config.symbol}] Failed to place order")
        state.reset_for_new_cycle()
        return False


# ============================================================================
# MAIN EXECUTION LOOP (Multi-Symbol)
# ============================================================================

def main():
    """Main trading loop for multiple symbols."""
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("MULTI-SYMBOL SMC TRADING ENGINE - STARTING")
    logger.info("=" * 80)
    
    # Initialize components
    feed = MT5DataFeed()
    symbol_manager = get_symbol_manager()
    
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
            
            # Get account info once per iteration
            account_info = feed.get_account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                time.sleep(config.SLEEP_INTERVAL)
                continue
            
            logger.info(f"Account Balance: ${account_info['balance']:.2f}")
            
            # Process each enabled symbol
            enabled_symbols = symbol_manager.get_all_enabled_symbols()
            logger.info(f"Processing {len(enabled_symbols)} symbol(s): {', '.join(enabled_symbols)}")
            
            for symbol_name in enabled_symbols:
                symbol_config = symbol_manager.get_symbol_config(symbol_name)
                if not symbol_config or not symbol_config.enabled:
                    continue
                
                logger.info(f"\n--- Processing {symbol_name} ---")
                
                # Set feed symbol
                feed.symbol = symbol_name
                executor = OrderExecutor(symbol=symbol_name)
                
                # Fetch data for this symbol
                data = {}
                try:
                    data['MAIN'] = feed.fetch_ohlcv(
                        config.get_timeframe_constant(symbol_config.main_timeframe)
                    )
                    data['CONF'] = feed.fetch_ohlcv(
                        config.get_timeframe_constant(symbol_config.conf_timeframe)
                    )
                    data['MINOR'] = feed.fetch_ohlcv(
                        config.get_timeframe_constant(symbol_config.minor_timeframe)
                    )
                    data['ENTRY'] = feed.fetch_ohlcv(
                        config.get_timeframe_constant(symbol_config.entry_timeframe)
                    )
                except Exception as e:
                    logger.error(f"[{symbol_name}] Error fetching data: {e}")
                    continue
                
                if any(df is None for df in data.values()):
                    logger.error(f"[{symbol_name}] Failed to fetch complete data")
                    continue
                
                # Get state for this symbol
                state = symbol_config.state
                state.last_update = datetime.now()
                
                # Check for existing positions
                open_positions = executor.get_open_positions()
                if len(open_positions) > 0:
                    logger.info(f"[{symbol_name}] Active position - monitoring")
                    continue
                
                # Reset if position closed
                if state.position_open and len(open_positions) == 0:
                    logger.info(f"[{symbol_name}] Position closed - resetting")
                    state.reset_for_new_cycle()
                
                # Execute trading pipeline
                check_main_bos_for_symbol(state, data['MAIN'], symbol_config)
                update_main_range_for_symbol(state, data['MAIN'], data['CONF'], symbol_config)
                check_pullback_to_eq_for_symbol(state, data['MINOR'], symbol_config)
                track_minor_structure_for_symbol(state, data['MINOR'], symbol_config)
                check_minor_mss_for_symbol(state, data['MINOR'], symbol_config)
                prepare_entry_for_symbol(state, data['ENTRY'], executor, account_info, symbol_config)
                
                # Log status
                logger.info(f"[{symbol_name}] Bias: {state.bias.value} | Phase: {state.phase.value}")
            
            # Sleep until next iteration
            logger.info(f"\nSleeping for {config.SLEEP_INTERVAL} seconds...\n")
            time.sleep(config.SLEEP_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested by user")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    
    finally:
        feed.shutdown()
        logger.info("=" * 80)
        logger.info("MULTI-SYMBOL SMC TRADING ENGINE - STOPPED")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()
