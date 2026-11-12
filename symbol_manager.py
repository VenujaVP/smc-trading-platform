"""
Symbol Manager - Multi-Symbol Trading Configuration
Manages multiple trading pairs with individual settings and state tracking.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from state_machine import MarketState
import config

logger = logging.getLogger(__name__)


@dataclass
class SymbolConfig:
    """Configuration for individual trading symbol."""
    symbol: str
    main_timeframe: str = "H4"  # Main Market Structure timeframe
    minor_timeframe: str = "H1"  # Minor MSS timeframe
    conf_timeframe: str = "H1"   # Confirmation timeframe
    entry_timeframe: str = "M15"  # Entry timeframe
    
    main_pivot_lookback: int = 5
    minor_pivot_lookback: int = 2
    
    risk_percent: float = 1.0
    min_risk_reward: float = 3.0
    stop_loss_buffer_pips: int = 20
    
    enabled: bool = True
    
    # Runtime data
    state: Optional[MarketState] = None
    last_update: Optional[str] = None


class SymbolManager:
    """
    Manages multiple trading symbols with individual configurations and states.
    Allows running the SMC strategy on multiple pairs simultaneously.
    """
    
    def __init__(self):
        self.symbols: Dict[str, SymbolConfig] = {}
        self.active_symbol: Optional[str] = None
        logger.info("SymbolManager initialized")
    
    def add_symbol(self, 
                   symbol: str,
                   main_tf: str = "H4",
                   minor_tf: str = "H1",
                   enabled: bool = True) -> bool:
        """
        Add a new symbol to trade.
        
        Args:
            symbol: Trading symbol (e.g., "XAUUSD", "EURUSD")
            main_tf: Main Market Structure timeframe (default "H4")
            minor_tf: Minor MSS timeframe (default "H1")
            enabled: Whether to actively trade this symbol
        
        Returns:
            True if added successfully
        """
        try:
            if symbol in self.symbols:
                logger.warning(f"Symbol {symbol} already exists")
                return False
            
            symbol_config = SymbolConfig(
                symbol=symbol,
                main_timeframe=main_tf,
                minor_timeframe=minor_tf,
                enabled=enabled,
                state=MarketState()
            )
            
            self.symbols[symbol] = symbol_config
            
            # Set as active if it's the first symbol
            if self.active_symbol is None:
                self.active_symbol = symbol
            
            logger.info(f"Added symbol: {symbol} (Main: {main_tf}, Minor: {minor_tf})")
            return True
        
        except Exception as e:
            logger.error(f"Error adding symbol {symbol}: {e}")
            return False
    
    def remove_symbol(self, symbol: str) -> bool:
        """Remove a symbol from trading."""
        try:
            if symbol not in self.symbols:
                logger.warning(f"Symbol {symbol} not found")
                return False
            
            del self.symbols[symbol]
            
            # Update active symbol if needed
            if self.active_symbol == symbol:
                self.active_symbol = next(iter(self.symbols.keys())) if self.symbols else None
            
            logger.info(f"Removed symbol: {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Error removing symbol {symbol}: {e}")
            return False
    
    def get_symbol_config(self, symbol: str) -> Optional[SymbolConfig]:
        """Get configuration for a specific symbol."""
        return self.symbols.get(symbol)
    
    def set_active_symbol(self, symbol: str) -> bool:
        """
        Set the active symbol for GUI display.
        
        Args:
            symbol: Symbol to make active
        
        Returns:
            True if set successfully
        """
        if symbol not in self.symbols:
            logger.error(f"Symbol {symbol} not found")
            return False
        
        self.active_symbol = symbol
        logger.info(f"Active symbol set to: {symbol}")
        return True
    
    def get_active_symbol_config(self) -> Optional[SymbolConfig]:
        """Get the configuration of the currently active symbol."""
        if self.active_symbol:
            return self.symbols.get(self.active_symbol)
        return None
    
    def get_active_symbol_state(self) -> Optional[MarketState]:
        """Get the trading state of the currently active symbol."""
        config = self.get_active_symbol_config()
        if config:
            return config.state
        return None
    
    def get_all_enabled_symbols(self) -> List[str]:
        """Get list of all enabled symbols."""
        return [sym for sym, cfg in self.symbols.items() if cfg.enabled]
    
    def get_all_symbols(self) -> List[str]:
        """Get list of all symbols (enabled and disabled)."""
        return list(self.symbols.keys())
    
    def update_symbol_timeframes(self, 
                                  symbol: str,
                                  main_tf: Optional[str] = None,
                                  minor_tf: Optional[str] = None) -> bool:
        """
        Update timeframes for a specific symbol.
        
        Args:
            symbol: Trading symbol
            main_tf: New Main Market Structure timeframe
            minor_tf: New Minor MSS timeframe
        
        Returns:
            True if updated successfully
        """
        try:
            if symbol not in self.symbols:
                logger.error(f"Symbol {symbol} not found")
                return False
            
            config = self.symbols[symbol]
            
            if main_tf:
                config.main_timeframe = main_tf
                logger.info(f"{symbol}: Main timeframe updated to {main_tf}")
            
            if minor_tf:
                config.minor_timeframe = minor_tf
                logger.info(f"{symbol}: Minor timeframe updated to {minor_tf}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating timeframes for {symbol}: {e}")
            return False
    
    def update_symbol_risk(self,
                           symbol: str,
                           risk_percent: Optional[float] = None,
                           min_rr: Optional[float] = None,
                           sl_buffer: Optional[int] = None) -> bool:
        """
        Update risk parameters for a specific symbol.
        
        Args:
            symbol: Trading symbol
            risk_percent: Risk per trade (%)
            min_rr: Minimum R:R ratio
            sl_buffer: Stop loss buffer (pips)
        
        Returns:
            True if updated successfully
        """
        try:
            if symbol not in self.symbols:
                logger.error(f"Symbol {symbol} not found")
                return False
            
            config = self.symbols[symbol]
            
            if risk_percent is not None:
                config.risk_percent = risk_percent
            
            if min_rr is not None:
                config.min_risk_reward = min_rr
            
            if sl_buffer is not None:
                config.stop_loss_buffer_pips = sl_buffer
            
            logger.info(f"{symbol}: Risk parameters updated")
            return True
        
        except Exception as e:
            logger.error(f"Error updating risk for {symbol}: {e}")
            return False
    
    def enable_symbol(self, symbol: str) -> bool:
        """Enable trading for a symbol."""
        if symbol in self.symbols:
            self.symbols[symbol].enabled = True
            logger.info(f"Symbol {symbol} enabled")
            return True
        return False
    
    def disable_symbol(self, symbol: str) -> bool:
        """Disable trading for a symbol."""
        if symbol in self.symbols:
            self.symbols[symbol].enabled = False
            logger.info(f"Symbol {symbol} disabled")
            return True
        return False
    
    def get_symbol_summary(self, symbol: str) -> Optional[Dict]:
        """
        Get summary information for a symbol.
        
        Returns:
            Dictionary with symbol config and state info
        """
        config = self.get_symbol_config(symbol)
        if not config:
            return None
        
        state_summary = config.state.get_status_summary() if config.state else {}
        
        return {
            'symbol': config.symbol,
            'enabled': config.enabled,
            'main_timeframe': config.main_timeframe,
            'minor_timeframe': config.minor_timeframe,
            'risk_percent': config.risk_percent,
            'min_risk_reward': config.min_risk_reward,
            'bias': state_summary.get('bias', 'NEUTRAL'),
            'phase': state_summary.get('phase', 'WAITING'),
            'main_range_valid': state_summary.get('main_range_valid', False),
            'minor_mss_confirmed': state_summary.get('minor_mss_confirmed', False),
            'entry_active': state_summary.get('entry_active', False),
            'position_open': state_summary.get('position_open', False)
        }
    
    def get_all_symbols_summary(self) -> List[Dict]:
        """Get summary for all symbols."""
        summaries = []
        for symbol in self.symbols.keys():
            summary = self.get_symbol_summary(symbol)
            if summary:
                summaries.append(summary)
        return summaries


# Global symbol manager instance
_symbol_manager = None

def get_symbol_manager() -> SymbolManager:
    """Get the global symbol manager instance."""
    global _symbol_manager
    if _symbol_manager is None:
        _symbol_manager = SymbolManager()
        # Add default symbol
        _symbol_manager.add_symbol("XAUUSD", main_tf="H4", minor_tf="H1", enabled=True)
    return _symbol_manager


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Symbol Manager...\n")
    
    manager = SymbolManager()
    
    # Add symbols
    manager.add_symbol("XAUUSD", main_tf="H4", minor_tf="H1")
    manager.add_symbol("EURUSD", main_tf="H1", minor_tf="M30")
    manager.add_symbol("GBPUSD", main_tf="H4", minor_tf="H1")
    
    print(f"✓ Active symbols: {manager.get_all_symbols()}")
    print(f"✓ Enabled symbols: {manager.get_all_enabled_symbols()}")
    
    # Set active symbol
    manager.set_active_symbol("EURUSD")
    print(f"✓ Active symbol: {manager.active_symbol}")
    
    # Update timeframes
    manager.update_symbol_timeframes("XAUUSD", main_tf="D1", minor_tf="H4")
    
    # Get summary
    summary = manager.get_symbol_summary("XAUUSD")
    print(f"\n✓ XAUUSD Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Symbol Manager tests completed!")
