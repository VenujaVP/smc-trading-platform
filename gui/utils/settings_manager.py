"""
Settings Manager - Secure storage and retrieval of configuration
"""

import yaml
import os
from cryptography.fernet import Fernet
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

SETTINGS_DIR = Path("config")
SETTINGS_FILE = SETTINGS_DIR / "settings.yaml"
CREDENTIALS_FILE = SETTINGS_DIR / "credentials.enc"
KEY_FILE = SETTINGS_DIR / ".key"


def _ensure_settings_dir():
    """Ensure settings directory exists."""
    SETTINGS_DIR.mkdir(exist_ok=True)


def _get_or_create_key():
    """Get or create encryption key."""
    _ensure_settings_dir()
    
    if KEY_FILE.exists():
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key


def _encrypt_data(data: str) -> bytes:
    """Encrypt sensitive data."""
    key = _get_or_create_key()
    f = Fernet(key)
    return f.encrypt(data.encode())


def _decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt sensitive data."""
    key = _get_or_create_key()
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()


def save_mt5_settings(account, password, server, symbol):
    """
    Save MT5 connection settings securely.
    """
    try:
        _ensure_settings_dir()
        
        # Encrypt credentials
        credentials = f"{account}|{password}|{server}"
        encrypted_creds = _encrypt_data(credentials)
        
        with open(CREDENTIALS_FILE, 'wb') as f:
            f.write(encrypted_creds)
        
        # Save non-sensitive settings
        settings = load_settings()
        settings['mt5'] = {
            'symbol': symbol,
            'account': account,
            'server': server
        }
        
        with open(SETTINGS_FILE, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False)
        
        logger.info("MT5 settings saved successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error saving MT5 settings: {e}")
        return False


def load_mt5_credentials():
    """
    Load MT5 credentials securely.
    
    Returns:
        dict with account, password, server, symbol
    """
    try:
        if not CREDENTIALS_FILE.exists():
            return None
        
        with open(CREDENTIALS_FILE, 'rb') as f:
            encrypted_creds = f.read()
        
        decrypted = _decrypt_data(encrypted_creds)
        account, password, server = decrypted.split('|')
        
        settings = load_settings()
        symbol = settings.get('mt5', {}).get('symbol', 'XAUUSD')
        
        return {
            'account': int(account),
            'password': password,
            'server': server,
            'symbol': symbol
        }
    
    except Exception as e:
        logger.error(f"Error loading MT5 credentials: {e}")
        return None


def save_trading_parameters(risk_percent, min_rr, sl_buffer):
    """Save trading parameters."""
    try:
        _ensure_settings_dir()
        
        settings = load_settings()
        settings['trading'] = {
            'risk_percent': float(risk_percent),
            'min_risk_reward': float(min_rr),
            'stop_loss_buffer_pips': int(sl_buffer)
        }
        
        with open(SETTINGS_FILE, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False)
        
        logger.info("Trading parameters saved")
        return True
    
    except Exception as e:
        logger.error(f"Error saving trading parameters: {e}")
        return False


def load_settings():
    """Load all settings from YAML."""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}


def test_mt5_connection(account, password, server):
    """
    Test MT5 connection with provided credentials.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            return False, f"MT5 initialization failed: {mt5.last_error()}"
        
        authorized = mt5.login(int(account), password=password, server=server)
        
        if not authorized:
            mt5.shutdown()
            return False, f"Login failed: {mt5.last_error()}"
        
        account_info = mt5.account_info()
        mt5.shutdown()
        
        if account_info:
            return True, f"✓ Connection successful! Balance: ${account_info.balance:,.2f}"
        else:
            return False, "Connected but failed to retrieve account info"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


# Initialize with default settings if needed
def initialize_default_settings():
    """Create default settings file if it doesn't exist."""
    if not SETTINGS_FILE.exists():
        default_settings = {
            'mt5': {
                'symbol': 'XAUUSD',
                'account': None,
                'server': None
            },
            'trading': {
                'risk_percent': 1.0,
                'min_risk_reward': 3.0,
                'stop_loss_buffer_pips': 20,
                'main_pivot_lookback': 5,
                'minor_pivot_lookback': 2
            },
            'system': {
                'refresh_interval': 5,
                'candles_to_fetch': 500,
                'log_level': 'INFO',
                'magic_number': 234567,
                'auto_trade': False,
                'notifications': True
            }
        }
        
        _ensure_settings_dir()
        with open(SETTINGS_FILE, 'w') as f:
            yaml.dump(default_settings, f, default_flow_style=False)
        
        logger.info("Default settings initialized")
