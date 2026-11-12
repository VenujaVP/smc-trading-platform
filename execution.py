"""
Execution Module for Advanced MTF SMC Trading Engine
Handles order placement, position management, and risk calculations.
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class OrderExecutor:
    """
    Manages trade execution, position sizing, and order management.
    """
    
    def __init__(self, symbol=None):
        self.symbol = symbol or config.SYMBOL
        self.magic_number = config.MAGIC_NUMBER
        
    def calculate_position_size(self, account_balance, entry_price, stop_loss, risk_percent=None):
        """
        Calculate position size based on account risk percentage.
        
        Args:
            account_balance: Current account balance
            entry_price: Entry price level
            stop_loss: Stop loss price level
            risk_percent: Risk percentage (default from config)
        
        Returns:
            Lot size to trade
        """
        if risk_percent is None:
            risk_percent = config.RISK_PERCENT
        
        # Calculate risk amount in account currency
        risk_amount = account_balance * (risk_percent / 100.0)
        
        # Calculate price risk (distance from entry to SL)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            logger.error("Price risk is zero - cannot calculate position size")
            return 0.0
        
        # Get symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Failed to get symbol info for {self.symbol}")
            return 0.0
        
        # Calculate pip value
        point = symbol_info.point
        pip_value = point * 10 if "XAU" in self.symbol or "GOLD" in self.symbol else point
        
        # Calculate risk in pips
        risk_pips = price_risk / pip_value
        
        # Calculate lot size
        # For forex: pip_value_per_lot = (pip_size * lot_size * contract_size) / quote_currency
        # Simplified: lots = risk_amount / (risk_pips * value_per_pip_per_lot)
        
        # Standard lot pip value (approximate - varies by broker)
        if "XAU" in self.symbol:
            pip_value_per_standard_lot = 1.0  # $1 per pip for gold mini lot
        else:
            pip_value_per_standard_lot = 10.0  # $10 per pip for forex standard lot
        
        lots = risk_amount / (risk_pips * pip_value_per_standard_lot)
        
        # Round to broker's lot step
        lot_step = symbol_info.volume_step
        lots = round(lots / lot_step) * lot_step
        
        # Check min/max lot sizes
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        
        lots = max(min_lot, min(lots, max_lot))
        
        logger.info(f"Position size calculated: {lots} lots | Risk: ${risk_amount:.2f} | Risk pips: {risk_pips:.1f}")
        return lots
    
    def calculate_risk_reward_ratio(self, entry_price, stop_loss, take_profit):
        """
        Calculate the risk-to-reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            R:R ratio as float (e.g., 3.0 for 1:3)
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            logger.error("Risk is zero - cannot calculate R:R")
            return 0.0
        
        rr_ratio = reward / risk
        logger.info(f"Risk:Reward ratio: 1:{rr_ratio:.2f}")
        return rr_ratio
    
    def validate_trade_setup(self, entry_price, stop_loss, take_profit, account_balance):
        """
        Validate trade setup before execution.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            account_balance: Account balance
        
        Returns:
            (is_valid, reason) tuple
        """
        # Check R:R ratio
        rr = self.calculate_risk_reward_ratio(entry_price, stop_loss, take_profit)
        if rr < config.MIN_RISK_REWARD:
            return False, f"R:R ratio {rr:.2f} below minimum {config.MIN_RISK_REWARD}"
        
        # Check price validity
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return False, "Invalid price levels"
        
        # Check symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return False, f"Cannot get symbol info for {self.symbol}"
        
        # Check if trading is allowed
        if not symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
            return False, f"Trading not allowed for {self.symbol}"
        
        return True, "Trade setup valid"
    
    def place_buy_limit(self, entry_price, stop_loss, take_profit, lot_size, comment=None):
        """
        Place a BUY LIMIT order with DUPLICATE PREVENTION.
        
        Args:
            entry_price: Limit order price
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Position size in lots
            comment: Order comment
        
        Returns:
            OrderSendResult object or None
        """
        # CRITICAL: Check for existing pending orders FIRST (duplicate prevention)
        existing_orders = self.get_pending_orders()
        if len(existing_orders) > 0:
            logger.warning(f"[{self.symbol}] Pending order already exists - skipping duplicate")
            for order in existing_orders:
                logger.info(f"  Existing: {order.type} @ {order.price_open} | Ticket: {order.ticket}")
            return None
        
        # Check for existing open positions
        existing_positions = self.get_open_positions()
        if len(existing_positions) > 0:
            logger.warning(f"[{self.symbol}] Position already open - skipping duplicate")
            return None
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found")
            return None
        
        # Normalize prices
        entry_price = round(entry_price, symbol_info.digits)
        stop_loss = round(stop_loss, symbol_info.digits)
        take_profit = round(take_profit, symbol_info.digits)
        
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": config.SLIPPAGE_POINTS,
            "magic": self.magic_number,
            "comment": comment or config.ORDER_COMMENT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        logger.info(f"[{self.symbol}] Placing BUY LIMIT: {lot_size} lots @ {entry_price} | SL: {stop_loss} | TP: {take_profit}")
        
        result = mt5.order_send(request)
        
        if result is None:
            logger.error(f"Order send failed: {mt5.last_error()}")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        logger.info(f"✓ [{self.symbol}] BUY LIMIT placed | Order: {result.order}")
        return result
    
    def place_sell_limit(self, entry_price, stop_loss, take_profit, lot_size, comment=None):
        """
        Place a SELL LIMIT order with DUPLICATE PREVENTION.
        
        Args:
            entry_price: Limit order price
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Position size in lots
            comment: Order comment
        
        Returns:
            OrderSendResult object or None
        """
        # CRITICAL: Check for existing pending orders FIRST (duplicate prevention)
        existing_orders = self.get_pending_orders()
        if len(existing_orders) > 0:
            logger.warning(f"[{self.symbol}] Pending order already exists - skipping duplicate")
            for order in existing_orders:
                logger.info(f"  Existing: {order.type} @ {order.price_open} | Ticket: {order.ticket}")
            return None
        
        # Check for existing open positions
        existing_positions = self.get_open_positions()
        if len(existing_positions) > 0:
            logger.warning(f"[{self.symbol}] Position already open - skipping duplicate")
            return None
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found")
            return None
        
        # Normalize prices
        entry_price = round(entry_price, symbol_info.digits)
        stop_loss = round(stop_loss, symbol_info.digits)
        take_profit = round(take_profit, symbol_info.digits)
        
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": config.SLIPPAGE_POINTS,
            "magic": self.magic_number,
            "comment": comment or config.ORDER_COMMENT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        logger.info(f"[{self.symbol}] Placing SELL LIMIT: {lot_size} lots @ {entry_price} | SL: {stop_loss} | TP: {take_profit}")
        
        result = mt5.order_send(request)
        
        if result is None:
            logger.error(f"Order send failed: {mt5.last_error()}")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        logger.info(f"✓ [{self.symbol}] SELL LIMIT placed | Order: {result.order}")
        return result
    
    def get_open_positions(self):
        """
        Get all open positions for this bot (by magic number).
        
        Returns:
            List of position objects
        """
        positions = mt5.positions_get(symbol=self.symbol)
        
        if positions is None:
            logger.error(f"Failed to get positions: {mt5.last_error()}")
            return []
        
        # Filter by magic number
        bot_positions = [pos for pos in positions if pos.magic == self.magic_number]
        return bot_positions
    
    def get_pending_orders(self):
        """
        Get all pending orders for this bot (by magic number).
        
        Returns:
            List of order objects
        """
        orders = mt5.orders_get(symbol=self.symbol)
        
        if orders is None:
            logger.error(f"Failed to get orders: {mt5.last_error()}")
            return []
        
        # Filter by magic number
        bot_orders = [order for order in orders if order.magic == self.magic_number]
        return bot_orders
    
    def close_all_positions(self):
        """
        Close all open positions for this bot.
        
        Returns:
            Number of positions closed
        """
        positions = self.get_open_positions()
        closed_count = 0
        
        for position in positions:
            # Determine order type
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": config.SLIPPAGE_POINTS,
                "magic": self.magic_number,
                "comment": "Close by bot",
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed_count += 1
                logger.info(f"Closed position {position.ticket}")
            else:
                logger.error(f"Failed to close position {position.ticket}")
        
        return closed_count
    
    def cancel_all_pending_orders(self):
        """
        Cancel all pending orders for this bot.
        
        Returns:
            Number of orders cancelled
        """
        orders = self.get_pending_orders()
        cancelled_count = 0
        
        for order in orders:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                cancelled_count += 1
                logger.info(f"Cancelled order {order.ticket}")
            else:
                logger.error(f"Failed to cancel order {order.ticket}")
        
        return cancelled_count


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Execution Module...\n")
    
    executor = OrderExecutor()
    
    # Test position size calculation
    account_balance = 10000.0
    entry_price = 2000.0
    stop_loss = 1980.0
    
    lot_size = executor.calculate_position_size(account_balance, entry_price, stop_loss)
    print(f"✓ Calculated lot size: {lot_size}")
    
    # Test R:R calculation
    take_profit = 2060.0
    rr = executor.calculate_risk_reward_ratio(entry_price, stop_loss, take_profit)
    print(f"✓ Risk:Reward ratio: 1:{rr:.2f}")
    
    # Test validation
    is_valid, reason = executor.validate_trade_setup(entry_price, stop_loss, take_profit, account_balance)
    print(f"✓ Trade validation: {is_valid} - {reason}")
    
    print("\nExecution Module tests completed successfully!")
    print("\nNote: Actual order placement requires MT5 connection and will not be tested here.")
