"""
Professional SMC Trading Platform Launcher
Main entry point for the complete trading system.
"""

import sys
import logging
import threading
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smc_platform.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def initialize_system():
    """Initialize all system components."""
    logger.info("="*80)
    logger.info("SMC TRADING PLATFORM - PROFESSIONAL EDITION")
    logger.info("="*80)
    
    # Initialize settings
    from gui.utils.settings_manager import initialize_default_settings
    initialize_default_settings()
    logger.info("✓ Settings system initialized")
    
    # Initialize MT5 interface
    from gui.utils.mt5_interface import initialize_mt5_interface
    if initialize_mt5_interface():
        logger.info("✓ MT5 interface initialized")
    else:
        logger.warning("⚠ MT5 interface not initialized - configure in settings")
    
    logger.info("✓ System initialization complete")


def run_trading_engine():
    """Run the trading engine in background."""
    try:
        from main import main as trading_main
        logger.info("Starting trading engine...")
        trading_main()
    except Exception as e:
        logger.error(f"Trading engine error: {e}")


def run_dashboard():
    """Run the dashboard GUI."""
    try:
        from gui.app import run_dashboard
        logger.info("Starting dashboard server...")
        run_dashboard(host='127.0.0.1', port=8050, debug=False)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")


def main():
    """Main application entry point."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         SMC TRADING PLATFORM - PROFESSIONAL EDITION          ║
    ║                                                              ║
    ║  Advanced Multi-Timeframe Smart Money Concepts Bot           ║
    ║  with Real-Time Visualization & Complete Management          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\n🚀 Initializing system...\n")
    
    # Initialize system
    initialize_system()
    
    print("\n" + "="*60)
    print("LAUNCH OPTIONS:")
    print("="*60)
    print("1. Dashboard Only (Visualization & Settings)")
    print("2. Trading Engine Only (Automated Trading)")
    print("3. Complete System (Dashboard + Trading Engine)")
    print("4. Exit")
    print("="*60)
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        print("\n📊 Launching Dashboard...")
        print("\n🌐 Dashboard will be available at: http://127.0.0.1:8050")
        print("   Press CTRL+C to stop\n")
        run_dashboard()
    
    elif choice == '2':
        print("\n🤖 Launching Trading Engine...")
        print("\nOptions:")
        print("  a) Single Symbol Mode (original)")
        print("  b) Multi-Symbol Mode (trade multiple pairs)")
        
        sub_choice = input("\nSelect (a/b): ").strip().lower()
        
        if sub_choice == 'b':
            print("\n📊 Multi-Symbol Trading Engine")
            print("   Configure symbols in Settings or symbol_manager.py")
            print("   Press CTRL+C to stop\n")
            from main_multi_symbol import main as multi_main
            multi_main()
        else:
            print("\n📊 Single Symbol Trading Engine")
            print("   Press CTRL+C to stop\n")
            run_trading_engine()
    
    elif choice == '3':
        print("\n🚀 Launching Complete System...")
        print("\n🌐 Dashboard: http://127.0.0.1:8050")
        print("🤖 Trading Engine: Running in background")
        print("   Press CTRL+C to stop both\n")
        
        # Start trading engine in separate thread
        engine_thread = threading.Thread(target=run_trading_engine, daemon=True)
        engine_thread.start()
        
        # Give engine time to start
        time.sleep(2)
        
        # Run dashboard in main thread
        run_dashboard()
    
    elif choice == '4':
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid option. Exiting.\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹  Shutdown requested by user")
        print("   Cleaning up...\n")
        logger.info("System shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
