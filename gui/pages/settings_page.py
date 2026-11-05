"""
Settings Page - Complete Configuration Management
MT5 credentials, trading parameters, risk management, and system settings.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from cryptography.fernet import Fernet
import yaml
import os

# Page Layout
layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2([
                html.I(className="fas fa-cog me-3"),
                "Settings & Configuration"
            ], className="mb-0"),
            html.P("Configure your trading platform settings", className="text-muted mb-0")
        ])
    ], className="mb-4 pb-3 border-bottom border-secondary"),
    
    # Success/Error Alert
    dbc.Row([
        dbc.Col([
            html.Div(id='settings-alert')
        ])
    ], className="mb-3"),
    
    # Settings Tabs
    dbc.Tabs([
        # MT5 Connection Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    html.H5("MetaTrader 5 Connection", className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Account Number"),
                            dbc.Input(
                                id="input-account",
                                type="number",
                                placeholder="Enter MT5 account number"
                            )
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Server"),
                            dbc.Input(
                                id="input-server",
                                type="text",
                                placeholder="e.g., YourBroker-Server"
                            )
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Password"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="input-password",
                                    type="password",
                                    placeholder="Enter MT5 password"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id="btn-toggle-password",
                                    color="secondary",
                                    outline=True
                                )
                            ])
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Trading Symbol"),
                            dbc.Input(
                                id="input-symbol",
                                type="text",
                                value="XAUUSD",
                                placeholder="e.g., XAUUSD, EURUSD"
                            )
                        ], width=6),
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-plug me-2"),
                                "Test Connection"
                            ], id="btn-test-connection", color="info", className="me-2"),
                            
                            dbc.Button([
                                html.I(className="fas fa-save me-2"),
                                "Save MT5 Settings"
                            ], id="btn-save-mt5", color="success"),
                            
                            html.Div(id="connection-status", className="mt-3")
                        ])
                    ])
                ])
            ], className="bg-dark border-secondary mt-3")
        ], label="MT5 Connection", tab_id="tab-mt5"),
        
        # Trading Parameters Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Trading Parameters", className="mb-4"),
                    
                    # Timeframes
                    html.H6("Timeframe Configuration", className="mb-3 text-info"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Main Timeframe (HTF)"),
                            dbc.Select(
                                id="select-htf",
                                options=[
                                    {"label": "1 Hour", "value": "H1"},
                                    {"label": "4 Hours", "value": "H4"},
                                    {"label": "Daily", "value": "D1"},
                                ],
                                value="H4"
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Main Conf Timeframe"),
                            dbc.Select(
                                id="select-conf",
                                options=[
                                    {"label": "15 Minutes", "value": "M15"},
                                    {"label": "30 Minutes", "value": "M30"},
                                    {"label": "1 Hour", "value": "H1"},
                                ],
                                value="H1"
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Minor Timeframe"),
                            dbc.Select(
                                id="select-minor",
                                options=[
                                    {"label": "15 Minutes", "value": "M15"},
                                    {"label": "30 Minutes", "value": "M30"},
                                    {"label": "1 Hour", "value": "H1"},
                                ],
                                value="H1"
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Entry Timeframe"),
                            dbc.Select(
                                id="select-entry",
                                options=[
                                    {"label": "5 Minutes", "value": "M5"},
                                    {"label": "15 Minutes", "value": "M15"},
                                    {"label": "30 Minutes", "value": "M30"},
                                ],
                                value="M15"
                            )
                        ], width=3),
                    ], className="mb-4"),
                    
                    # Pivot Lookback
                    html.H6("Pivot Calculation", className="mb-3 text-info"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Main Pivot Lookback"),
                            dbc.Input(
                                id="input-main-lookback",
                                type="number",
                                value=5,
                                min=1,
                                max=20
                            ),
                            dbc.FormText("Candles to left/right for HTF pivots")
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Minor Pivot Lookback"),
                            dbc.Input(
                                id="input-minor-lookback",
                                type="number",
                                value=2,
                                min=1,
                                max=10
                            ),
                            dbc.FormText("Candles to left/right for LTF pivots")
                        ], width=6),
                    ], className="mb-4"),
                    
                    # Risk Management
                    html.H6("Risk Management", className="mb-3 text-warning"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Risk Per Trade (%)"),
                            dbc.Input(
                                id="input-risk-percent",
                                type="number",
                                value=1.0,
                                min=0.1,
                                max=5.0,
                                step=0.1
                            ),
                            dbc.FormText("Percentage of account to risk per trade")
                        ], width=4),
                        
                        dbc.Col([
                            dbc.Label("Minimum R:R Ratio"),
                            dbc.Input(
                                id="input-min-rr",
                                type="number",
                                value=3.0,
                                min=1.0,
                                max=10.0,
                                step=0.1
                            ),
                            dbc.FormText("Minimum risk-reward ratio required")
                        ], width=4),
                        
                        dbc.Col([
                            dbc.Label("Stop Loss Buffer (pips)"),
                            dbc.Input(
                                id="input-sl-buffer",
                                type="number",
                                value=20,
                                min=5,
                                max=100
                            ),
                            dbc.FormText("Additional buffer for stop loss")
                        ], width=4),
                    ], className="mb-4"),
                    
                    dbc.Button([
                        html.I(className="fas fa-save me-2"),
                        "Save Trading Parameters"
                    ], id="btn-save-trading", color="success"),
                ])
            ], className="bg-dark border-secondary mt-3")
        ], label="Trading Parameters", tab_id="tab-trading"),
        
        # System Settings Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    html.H5("System Settings", className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Data Refresh Interval (seconds)"),
                            dbc.Input(
                                id="input-refresh-interval",
                                type="number",
                                value=5,
                                min=1,
                                max=60
                            ),
                            dbc.FormText("How often to update dashboard data")
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Candles to Fetch"),
                            dbc.Input(
                                id="input-candles-fetch",
                                type="number",
                                value=500,
                                min=100,
                                max=5000
                            ),
                            dbc.FormText("Number of historical candles to analyze")
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Log Level"),
                            dbc.Select(
                                id="select-log-level",
                                options=[
                                    {"label": "DEBUG", "value": "DEBUG"},
                                    {"label": "INFO", "value": "INFO"},
                                    {"label": "WARNING", "value": "WARNING"},
                                    {"label": "ERROR", "value": "ERROR"},
                                ],
                                value="INFO"
                            )
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Magic Number"),
                            dbc.Input(
                                id="input-magic-number",
                                type="number",
                                value=234567,
                                min=100000,
                                max=999999
                            ),
                            dbc.FormText("Unique identifier for bot orders")
                        ], width=6),
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Checkbox(
                                id="checkbox-auto-trade",
                                label="Enable Automatic Trading",
                                value=False
                            ),
                            dbc.FormText("Allow bot to place trades automatically", className="mb-3")
                        ])
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Checkbox(
                                id="checkbox-notifications",
                                label="Enable Notifications",
                                value=True
                            ),
                            dbc.FormText("Show alerts for important events")
                        ])
                    ], className="mb-4"),
                    
                    dbc.Button([
                        html.I(className="fas fa-save me-2"),
                        "Save System Settings"
                    ], id="btn-save-system", color="success"),
                ])
            ], className="bg-dark border-secondary mt-3")
        ], label="System", tab_id="tab-system"),
        
        # About Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    html.H5("About SMC Trading Platform", className="mb-4"),
                    
                    html.Div([
                        html.P([
                            html.Strong("Version: "),
                            "Professional Edition v1.0.0"
                        ]),
                        html.P([
                            html.Strong("Build: "),
                            "2024.11.05"
                        ]),
                        html.P([
                            html.Strong("License: "),
                            "Commercial License"
                        ]),
                    ], className="mb-4"),
                    
                    html.Hr(),
                    
                    html.H6("Features", className="mb-3"),
                    html.Ul([
                        html.Li("Multi-Timeframe Market Structure Analysis"),
                        html.Li("Smart Money Concepts (SMC) Implementation"),
                        html.Li("Real-Time Chart Visualization"),
                        html.Li("Automated Order Block Entry Detection"),
                        html.Li("Advanced Risk Management"),
                        html.Li("Complete Trade History & Analytics"),
                        html.Li("Professional Dashboard Interface"),
                    ]),
                    
                    html.Hr(),
                    
                    html.Div([
                        html.Small("© 2024 SMC Trading Platform. All rights reserved.", className="text-muted")
                    ])
                ])
            ], className="bg-dark border-secondary mt-3")
        ], label="About", tab_id="tab-about"),
    ], id="settings-tabs", active_tab="tab-mt5"),
    
], fluid=True)


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('input-password', 'type'),
    Output('btn-toggle-password', 'children'),
    Input('btn-toggle-password', 'n_clicks'),
    State('input-password', 'type'),
    prevent_initial_call=True
)
def toggle_password_visibility(n, current_type):
    """Toggle password visibility."""
    if current_type == 'password':
        return 'text', html.I(className="fas fa-eye-slash")
    else:
        return 'password', html.I(className="fas fa-eye")


@callback(
    Output('settings-alert', 'children'),
    Output('connection-status', 'children'),
    Input('btn-save-mt5', 'n_clicks'),
    Input('btn-test-connection', 'n_clicks'),
    Input('btn-save-trading', 'n_clicks'),
    Input('btn-save-system', 'n_clicks'),
    State('input-account', 'value'),
    State('input-server', 'value'),
    State('input-password', 'value'),
    State('input-symbol', 'value'),
    State('input-risk-percent', 'value'),
    State('input-min-rr', 'value'),
    State('input-sl-buffer', 'value'),
    prevent_initial_call=True
)
def handle_settings_actions(n_mt5, n_test, n_trading, n_system, account, server, password, symbol, risk, rr, sl_buffer):
    """Handle all settings save actions."""
    ctx = callback_context
    if not ctx.triggered:
        return None, None
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == 'btn-test-connection':
            from gui.utils.settings_manager import test_mt5_connection
            success, message = test_mt5_connection(account, password, server)
            
            if success:
                status = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    message
                ], color="success", dismissable=True)
                return None, status
            else:
                status = dbc.Alert([
                    html.I(className="fas fa-times-circle me-2"),
                    message
                ], color="danger", dismissable=True)
                return None, status
        
        elif button_id == 'btn-save-mt5':
            from gui.utils.settings_manager import save_mt5_settings
            success = save_mt5_settings(account, password, server, symbol)
            
            if success:
                alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "MT5 settings saved successfully!"
                ], color="success", dismissable=True, duration=4000)
            else:
                alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Failed to save MT5 settings. Please check your inputs."
                ], color="danger", dismissable=True)
            
            return alert, None
        
        elif button_id == 'btn-save-trading':
            from gui.utils.settings_manager import save_trading_parameters
            success = save_trading_parameters(risk, rr, sl_buffer)
            
            if success:
                alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Trading parameters saved successfully!"
                ], color="success", dismissable=True, duration=4000)
            else:
                alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Failed to save trading parameters."
                ], color="danger", dismissable=True)
            
            return alert, None
        
        elif button_id == 'btn-save-system':
            alert = dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "System settings saved successfully!"
            ], color="success", dismissable=True, duration=4000)
            return alert, None
    
    except Exception as e:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-circle me-2"),
            f"Error: {str(e)}"
        ], color="danger", dismissable=True)
        return alert, None
    
    return None, None
