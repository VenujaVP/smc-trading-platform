"""
MT5 Interface - Bridge between GUI and MT5 trading engine
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import logging
from state_machine import MarketState
from data_feed import MT5DataFeed
from gui.utils.settings_manager import load_mt5_credentials, load_settings

logger = logging.getLogger(__name__)

# Global instances
_feed = None
_state = None


def initialize_mt5_interface():
    """Initialize MT5 connection and state machine."""
    global _feed, _state
    
    try:
        credentials = load_mt5_credentials()
        if not credentials:
            logger.warning("No MT5 credentials found")
            return False
        
        _feed = MT5DataFeed()
        if not _feed.initialize():
            logger.error("Failed to initialize MT5 feed")
            return False
        
        _state = MarketState()
        logger.info("MT5 interface initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing MT5 interface: {e}")
        return False


def get_system_status():
    """Get current system connection status."""
    try:
        if _feed and _feed.connected:
            return {
                'connected': True,
                'timestamp': datetime.now()
            }
        return {'connected': False}
    except:
        return {'connected': False}


def get_account_summary():
    """Get account summary information."""
    try:
        if not _feed or not _feed.connected:
            return None
        
        account_info = _feed.get_account_info()
        if not account_info:
            return None
        
        # Calculate daily P/L (simplified - would need trade history)
        daily_pnl = account_info['profit']
        
        # Calculate margin usage
        margin_usage = 0
        if account_info['equity'] > 0:
            margin_usage = (account_info['margin'] / account_info['equity']) * 100
        
        # Get open positions count
        from execution import OrderExecutor
        executor = OrderExecutor()
        open_positions = len(executor.get_open_positions())
        
        return {
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'margin': account_info['margin'],
            'free_margin': account_info['free_margin'],
            'margin_usage': margin_usage,
            'daily_pnl': daily_pnl,
            'open_positions': open_positions
        }
    
    except Exception as e:
        logger.error(f"Error getting account summary: {e}")
        return None


def get_trading_state():
    """Get current trading state from state machine."""
    try:
        if not _state:
            return None
        
        status = _state.get_status_summary()
        
        # Calculate R:R ratio if entry setup exists
        rr_ratio = None
        if status['entry_active'] and _state.entry_price and _state.stop_loss and _state.take_profit:
            risk = abs(_state.entry_price - _state.stop_loss)
            reward = abs(_state.take_profit - _state.entry_price)
            if risk > 0:
                rr_ratio = reward / risk
        
        return {
            'bias': status['bias'],
            'phase': status['phase'],
            'main_range_high': status['main_range_high'],
            'main_range_low': status['main_range_low'],
            'equilibrium': status['equilibrium'],
            'watch_pivot': status['watch_pivot'],
            'tracked_extreme': status['tracked_extreme'],
            'minor_mss_confirmed': status['minor_mss_confirmed'],
            'entry_price': _state.entry_price,
            'stop_loss': _state.stop_loss,
            'take_profit': _state.take_profit,
            'rr_ratio': rr_ratio
        }
    
    except Exception as e:
        logger.error(f"Error getting trading state: {e}")
        return None


def get_open_positions_data():
    """Get open positions as DataFrame."""
    try:
        from execution import OrderExecutor
        executor = OrderExecutor()
        positions = executor.get_open_positions()
        
        if not positions or len(positions) == 0:
            return None
        
        data = []
        for pos in positions:
            data.append({
                'Ticket': pos.ticket,
                'Type': 'BUY' if pos.type == 0 else 'SELL',
                'Volume': pos.volume,
                'Entry': f"{pos.price_open:.2f}",
                'Current': f"{pos.price_current:.2f}",
                'S/L': f"{pos.sl:.2f}" if pos.sl else '--',
                'T/P': f"{pos.tp:.2f}" if pos.tp else '--',
                'Profit': f"${pos.profit:.2f}",
                'Time': datetime.fromtimestamp(pos.time).strftime('%Y-%m-%d %H:%M')
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        logger.error(f"Error getting positions data: {e}")
        return None


def get_recent_activity(limit=10):
    """Get recent trading activity log."""
    try:
        # This would normally read from a log file or database
        # For now, return dummy data
        activities = [
            {
                'time': datetime.now().strftime('%H:%M:%S'),
                'message': 'System initialized',
                'type': 'info'
            },
            {
                'time': (datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S'),
                'message': 'Checking for Main BOS...',
                'type': 'info'
            }
        ]
        
        return activities[:limit]
    
    except Exception as e:
        logger.error(f"Error getting activity log: {e}")
        return []


def get_market_data(timeframe='H4', count=500):
    """Get market data for charting."""
    try:
        if not _feed or not _feed.connected:
            return None
        
        # Map timeframe string to MT5 constant
        tf_map = {
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H4)
        df = _feed.fetch_ohlcv(mt5_tf, count=count)
        
        return df
    
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return None
