"""
Main Dashboard Application - Professional SMC Trading Platform
Advanced GUI with real-time visualization, market structure analysis, and complete trading management.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize Dash app with professional theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="SMC Trading Platform | Professional Edition"
)

# App layout with sidebar navigation
app.layout = dbc.Container([
    dcc.Store(id='app-state', data={}),
    dcc.Store(id='settings-store', data={}),
    dcc.Interval(id='data-refresh-interval', interval=5000, n_intervals=0),  # 5 second refresh
    
    dbc.Row([
        # Sidebar Navigation
        dbc.Col([
            html.Div([
                # Logo/Brand
                html.Div([
                    html.I(className="fas fa-chart-line fa-2x mb-2", style={'color': '#00d4ff'}),
                    html.H4("SMC Platform", className="text-center mb-4", style={'color': '#00d4ff'}),
                ], className="text-center py-4 border-bottom border-secondary"),
                
                # Navigation Menu
                dbc.Nav([
                    dbc.NavLink([
                        html.I(className="fas fa-home me-2"),
                        "Dashboard"
                    ], href="/", id="nav-dashboard", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-layer-group me-2"),
                        "Pairs Manager"
                    ], href="/pairs", id="nav-pairs", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-chart-candlestick me-2"),
                        "Live Analysis"
                    ], href="/analysis", id="nav-analysis", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-exchange-alt me-2"),
                        "Trading Panel"
                    ], href="/trading", id="nav-trading", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-history me-2"),
                        "Trade History"
                    ], href="/history", id="nav-history", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-chart-bar me-2"),
                        "Performance"
                    ], href="/performance", id="nav-performance", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-layer-group me-2"),
                        "Symbols"
                    ], href="/symbols", id="nav-symbols", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-cog me-2"),
                        "Settings"
                    ], href="/settings", id="nav-settings", active="exact", className="mb-2"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-bell me-2"),
                        "Alerts"
                    ], href="/alerts", id="nav-alerts", active="exact", className="mb-2"),
                    
                ], vertical=True, pills=True, className="px-3"),
                
                # System Status
                html.Div([
                    html.Hr(className="my-4"),
                    html.Div([
                        html.Small("System Status", className="text-muted d-block mb-2"),
                        html.Div([
                            html.I(className="fas fa-circle me-2", id="status-indicator"),
                            html.Span("Initializing...", id="status-text")
                        ], className="d-flex align-items-center"),
                    ], className="px-3"),
                    
                    html.Hr(className="my-3"),
                    
                    # Quick Stats
                    html.Div([
                        html.Small("Quick Stats", className="text-muted d-block mb-2"),
                        html.Div([
                            html.Small("Balance:", className="text-muted me-2"),
                            html.Span("$0.00", id="sidebar-balance", className="text-success fw-bold")
                        ], className="mb-1"),
                        html.Div([
                            html.Small("Open Trades:", className="text-muted me-2"),
                            html.Span("0", id="sidebar-trades", className="text-info fw-bold")
                        ], className="mb-1"),
                        html.Div([
                            html.Small("Today P/L:", className="text-muted me-2"),
                            html.Span("$0.00", id="sidebar-pnl", className="fw-bold")
                        ]),
                    ], className="px-3"),
                ], className="mt-auto"),
                
            ], style={
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'bottom': 0,
                'width': '280px',
                'backgroundColor': '#1a1a1a',
                'borderRight': '1px solid #333',
                'overflowY': 'auto',
                'zIndex': 1000
            })
        ], width=0, style={'padding': 0}),
        
        # Main Content Area
        dbc.Col([
            html.Div([
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content')
            ], style={'marginLeft': '280px', 'padding': '20px'})
        ], width=12, style={'padding': 0}),
    ], className="g-0"),
    
], fluid=True, style={'padding': 0, 'backgroundColor': '#0d0d0d', 'minHeight': '100vh'})


# ============================================================================
# CALLBACK: Page Navigation
# ============================================================================
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages based on URL."""
    if pathname == '/analysis':
        from gui.pages import analysis_page
        return analysis_page.layout
    elif pathname == '/trading':
        from gui.pages import trading_page
        return trading_page.layout
    elif pathname == '/history':
        from gui.pages import history_page
        return history_page.layout
    elif pathname == '/performance':
        from gui.pages import performance_page
        return performance_page.layout
    elif pathname == '/symbols':
        from gui.pages import symbols_page
        return symbols_page.layout
    elif pathname == '/settings':
        from gui.pages import settings_page
        return settings_page.layout
    elif pathname == '/alerts':
        from gui.pages import alerts_page
        return alerts_page.layout
    else:
        from gui.pages import dashboard_page
        return dashboard_page.layout


# ============================================================================
# CALLBACK: System Status Update
# ============================================================================
@app.callback(
    [Output('status-indicator', 'style'),
     Output('status-text', 'children'),
     Output('sidebar-balance', 'children'),
     Output('sidebar-trades', 'children'),
     Output('sidebar-pnl', 'children'),
     Output('sidebar-pnl', 'style')],
    Input('data-refresh-interval', 'n_intervals')
)
def update_system_status(n):
    """Update system status and quick stats in sidebar."""
    try:
        from gui.utils.mt5_interface import get_system_status, get_account_summary
        
        status = get_system_status()
        account = get_account_summary()
        
        if status['connected']:
            indicator_style = {'color': '#00ff00', 'fontSize': '10px'}
            status_text = "Connected • Live"
        else:
            indicator_style = {'color': '#ff0000', 'fontSize': '10px'}
            status_text = "Disconnected"
        
        balance = f"${account['balance']:,.2f}" if account else "$0.00"
        trades = str(account['open_positions']) if account else "0"
        pnl = f"${account['daily_pnl']:,.2f}" if account else "$0.00"
        
        pnl_style = {
            'color': '#00ff00' if account and account['daily_pnl'] >= 0 else '#ff0000'
        }
        
        return indicator_style, status_text, balance, trades, pnl, pnl_style
        
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return (
            {'color': '#ff9900', 'fontSize': '10px'},
            "Error",
            "$0.00",
            "0",
            "$0.00",
            {}
        )


# ============================================================================
# Run Server
# ============================================================================
def run_dashboard(host='127.0.0.1', port=8050, debug=False):
    """Start the dashboard server."""
    logger.info(f"Starting dashboard server on http://{host}:{port}")
    app.run_server(host=host, port=port, debug=debug)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_dashboard(debug=True)
