"""
Data Feed Module for Advanced MTF SMC Trading Engine
Handles MT5 initialization, connection, and multi-timeframe data retrieval.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import logging
import config

logger = logging.getLogger(__name__)


class MT5DataFeed:
    """
    Manages connection to MT5 terminal and fetches OHLCV data
    for multiple timeframes concurrently.
    """
    
    def __init__(self):
        self.connected = False
        self.symbol = config.SYMBOL
        
    def initialize(self):
        """
        Initialize connection to MT5 terminal.
        Returns True if successful, False otherwise.
        """
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        
        logger.info("MT5 initialized successfully")
        
        # Authenticate
        authorized = mt5.login(
            config.MT5_ACCOUNT,
            password=config.MT5_PASSWORD,
            server=config.MT5_SERVER
        )
        
        if not authorized:
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        logger.info(f"MT5 logged in successfully to account {config.MT5_ACCOUNT}")
        
        # Enable symbol in Market Watch
        if not mt5.symbol_select(self.symbol, True):
            logger.error(f"Failed to select symbol {self.symbol}: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        # Store symbol info in config
        config.SYMBOL_INFO = mt5.symbol_info(self.symbol)
        if config.SYMBOL_INFO is None:
            logger.error(f"Failed to get symbol info for {self.symbol}")
            mt5.shutdown()
            return False
        
        logger.info(f"Symbol {self.symbol} selected and info loaded")
        self.connected = True
        return True
    
    def shutdown(self):
        """Gracefully shutdown MT5 connection."""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 connection closed")
    
    def fetch_ohlcv(self, timeframe, count=None):
        """
        Fetch OHLCV data for a specific timeframe.
        
        Args:
            timeframe: MT5 timeframe constant (e.g., mt5.TIMEFRAME_H4)
            count: Number of candles to fetch (default: from config)
        
        Returns:
            pandas.DataFrame with columns: time, open, high, low, close, volume
        """
        if not self.connected:
            logger.error("MT5 not connected. Call initialize() first.")
            return None
        
        if count is None:
            count = config.CANDLES_TO_FETCH
        
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
        
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to fetch data for timeframe {timeframe}: {mt5.last_error()}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        
        # Convert time to datetime
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Keep only relevant columns
        df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        
        logger.debug(f"Fetched {len(df)} candles for timeframe {timeframe}")
        return df
    
    def fetch_all_timeframes(self):
        """
        Fetch OHLCV data for all configured timeframes concurrently.
        
        Returns:
            Dictionary with keys: 'HTF', 'MAIN_CONF', 'MINOR', 'ENTRY'
            Each value is a pandas.DataFrame
        """
        if not self.connected:
            logger.error("MT5 not connected. Call initialize() first.")
            return None
        
        data = {}
        
        for tf_name, tf_value in config.TIMEFRAMES.items():
            df = self.fetch_ohlcv(tf_value)
            if df is None:
                logger.error(f"Failed to fetch data for {tf_name}")
                return None
            data[tf_name] = df
        
        logger.info("Successfully fetched all timeframe data")
        return data
    
    def get_account_info(self):
        """
        Get current account information.
        
        Returns:
            Dictionary with balance, equity, margin, free_margin
        """
        if not self.connected:
            logger.error("MT5 not connected")
            return None
        
        account_info = mt5.account_info()
        if account_info is None:
            logger.error(f"Failed to get account info: {mt5.last_error()}")
            return None
        
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'profit': account_info.profit
        }
    
    def get_current_price(self):
        """
        Get current bid/ask prices for the symbol.
        
        Returns:
            Dictionary with 'bid' and 'ask' prices
        """
        if not self.connected:
            logger.error("MT5 not connected")
            return None
        
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            logger.error(f"Failed to get tick data: {mt5.last_error()}")
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'time': datetime.fromtimestamp(tick.time)
        }


# ============================================================================
# MODULE TEST (Run this file directly to test connection)
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    feed = MT5DataFeed()
    
    if feed.initialize():
        print("✓ MT5 Connection Successful")
        
        # Test fetching all timeframes
        data = feed.fetch_all_timeframes()
        if data:
            print("\n✓ Data Fetch Successful:")
            for tf_name, df in data.items():
                print(f"  {tf_name}: {len(df)} candles")
                print(f"    Latest: {df.iloc[-1]['time']}")
        
        # Test account info
        account = feed.get_account_info()
        if account:
            print(f"\n✓ Account Info:")
            print(f"  Balance: ${account['balance']:.2f}")
            print(f"  Equity: ${account['equity']:.2f}")
        
        # Test current price
        price = feed.get_current_price()
        if price:
            print(f"\n✓ Current Price:")
            print(f"  Bid: {price['bid']}")
            print(f"  Ask: {price['ask']}")
        
        feed.shutdown()
    else:
        print("✗ MT5 Connection Failed")
