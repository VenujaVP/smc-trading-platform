"""
Main Dashboard Page - Overview and Real-Time Monitoring
"""

from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime

# Page Layout
layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2([
                html.I(className="fas fa-tachometer-alt me-3"),
                "Trading Dashboard"
            ], className="mb-0"),
            html.P(
                f"Real-time market analysis and trading overview",
                className="text-muted mb-0"
            )
        ], width=8),
        dbc.Col([
            html.Div([
                html.Span(id='dashboard-time', className="text-muted"),
            ], className="text-end")
        ], width=4)
    ], className="mb-4 pb-3 border-bottom border-secondary"),
    
    # Account Overview Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-wallet fa-2x text-primary"),
                    ], className="mb-2"),
                    html.H4("$0.00", id="card-balance", className="mb-0"),
                    html.Small("Account Balance", className="text-muted")
                ])
            ], className="text-center h-100 bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-2x text-success"),
                    ], className="mb-2"),
                    html.H4("$0.00", id="card-equity", className="mb-0"),
                    html.Small("Current Equity", className="text-muted")
                ])
            ], className="text-center h-100 bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-percentage fa-2x text-info"),
                    ], className="mb-2"),
                    html.H4("0.00%", id="card-margin", className="mb-0"),
                    html.Small("Margin Usage", className="text-muted")
                ])
            ], className="text-center h-100 bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-coins fa-2x text-warning"),
                    ], className="mb-2"),
                    html.H4("$0.00", id="card-pnl", className="mb-0"),
                    html.Small("Today's P/L", className="text-muted")
                ])
            ], className="text-center h-100 bg-dark border-secondary")
        ], width=3),
    ], className="mb-4"),
    
    # Market Structure Analysis
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-candlestick me-2"),
                    "Market Structure Analysis"
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='market-structure-chart',
                        config={'displayModeBar': True, 'displaylogo': False},
                        style={'height': '500px'}
                    )
                ])
            ], className="bg-dark border-secondary")
        ], width=8),
        
        # Trading State Panel
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-info-circle me-2"),
                    "Trading State"
                ]),
                dbc.CardBody([
                    # Market Bias
                    html.Div([
                        html.H6("Market Bias", className="text-muted mb-2"),
                        dbc.Badge("NEUTRAL", id="badge-bias", color="secondary", className="mb-3 px-3 py-2 fs-6")
                    ], className="mb-4"),
                    
                    # Current Phase
                    html.Div([
                        html.H6("Current Phase", className="text-muted mb-2"),
                        html.Div(id="current-phase", className="mb-3")
                    ], className="mb-4"),
                    
                    # Main Range
                    html.Div([
                        html.H6("Main Range", className="text-muted mb-2"),
                        html.Div([
                            html.Div([
                                html.Small("High: ", className="text-muted"),
                                html.Span("--", id="range-high", className="text-info")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("EQ: ", className="text-muted"),
                                html.Span("--", id="range-eq", className="text-warning")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("Low: ", className="text-muted"),
                                html.Span("--", id="range-low", className="text-info")
                            ]),
                        ])
                    ], className="mb-4"),
                    
                    # Minor Structure
                    html.Div([
                        html.H6("Minor Structure", className="text-muted mb-2"),
                        html.Div([
                            html.Div([
                                html.Small("Watch Pivot: ", className="text-muted"),
                                html.Span("--", id="watch-pivot", className="text-success")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("Tracked Extreme: ", className="text-muted"),
                                html.Span("--", id="tracked-extreme", className="text-success")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("MSS Status: ", className="text-muted"),
                                dbc.Badge("WAITING", id="mss-status", color="secondary", className="mt-1")
                            ]),
                        ])
                    ], className="mb-4"),
                    
                    # Entry Setup
                    html.Div([
                        html.H6("Entry Setup", className="text-muted mb-2"),
                        html.Div([
                            html.Div([
                                html.Small("Entry Price: ", className="text-muted"),
                                html.Span("--", id="entry-price", className="text-primary")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("Stop Loss: ", className="text-muted"),
                                html.Span("--", id="stop-loss", className="text-danger")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("Take Profit: ", className="text-muted"),
                                html.Span("--", id="take-profit", className="text-success")
                            ], className="mb-1"),
                            html.Div([
                                html.Small("R:R Ratio: ", className="text-muted"),
                                html.Span("--", id="rr-ratio", className="text-warning fw-bold")
                            ]),
                        ])
                    ]),
                ])
            ], className="bg-dark border-secondary h-100")
        ], width=4),
    ], className="mb-4"),
    
    # Open Positions
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-exchange-alt me-2"),
                    "Open Positions"
                ]),
                dbc.CardBody([
                    html.Div(id='open-positions-table')
                ])
            ], className="bg-dark border-secondary")
        ])
    ], className="mb-4"),
    
    # Recent Activity Log
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-list me-2"),
                    "Recent Activity"
                ]),
                dbc.CardBody([
                    html.Div(id='activity-log', style={'maxHeight': '200px', 'overflowY': 'auto'})
                ])
            ], className="bg-dark border-secondary")
        ])
    ]),
    
], fluid=True)


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('dashboard-time', 'children'),
    Input('data-refresh-interval', 'n_intervals')
)
def update_time(n):
    """Update current time display."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@callback(
    [Output('card-balance', 'children'),
     Output('card-equity', 'children'),
     Output('card-margin', 'children'),
     Output('card-pnl', 'children'),
     Output('card-pnl', 'style')],
    Input('data-refresh-interval', 'n_intervals')
)
def update_account_cards(n):
    """Update account overview cards."""
    try:
        from gui.utils.mt5_interface import get_account_summary
        account = get_account_summary()
        
        if account:
            balance = f"${account['balance']:,.2f}"
            equity = f"${account['equity']:,.2f}"
            margin = f"{account['margin_usage']:.1f}%"
            pnl = f"${account['daily_pnl']:,.2f}"
            pnl_style = {'color': '#00ff00' if account['daily_pnl'] >= 0 else '#ff0000'}
            
            return balance, equity, margin, pnl, pnl_style
    except:
        pass
    
    return "$0.00", "$0.00", "0.0%", "$0.00", {}


@callback(
    [Output('badge-bias', 'children'),
     Output('badge-bias', 'color'),
     Output('current-phase', 'children'),
     Output('range-high', 'children'),
     Output('range-eq', 'children'),
     Output('range-low', 'children'),
     Output('watch-pivot', 'children'),
     Output('tracked-extreme', 'children'),
     Output('mss-status', 'children'),
     Output('mss-status', 'color'),
     Output('entry-price', 'children'),
     Output('stop-loss', 'children'),
     Output('take-profit', 'children'),
     Output('rr-ratio', 'children')],
    Input('data-refresh-interval', 'n_intervals')
)
def update_trading_state(n):
    """Update trading state panel with current market structure."""
    try:
        from gui.utils.mt5_interface import get_trading_state
        state = get_trading_state()
        
        if state:
            # Bias
            bias_text = state['bias']
            bias_color = "success" if bias_text == "BULLISH" else "danger" if bias_text == "BEARISH" else "secondary"
            
            # Phase
            phase = html.Span(state['phase'], className="badge bg-info")
            
            # Ranges
            r_high = f"{state['main_range_high']:.2f}" if state['main_range_high'] else "--"
            r_eq = f"{state['equilibrium']:.2f}" if state['equilibrium'] else "--"
            r_low = f"{state['main_range_low']:.2f}" if state['equilibrium'] else "--"
            
            # Minor
            watch = f"{state['watch_pivot']:.2f}" if state['watch_pivot'] else "--"
            extreme = f"{state['tracked_extreme']:.2f}" if state['tracked_extreme'] else "--"
            mss_text = "CONFIRMED" if state['minor_mss_confirmed'] else "WAITING"
            mss_color = "success" if state['minor_mss_confirmed'] else "secondary"
            
            # Entry
            entry = f"{state['entry_price']:.2f}" if state['entry_price'] else "--"
            sl = f"{state['stop_loss']:.2f}" if state['stop_loss'] else "--"
            tp = f"{state['take_profit']:.2f}" if state['take_profit'] else "--"
            rr = f"1:{state['rr_ratio']:.1f}" if state['rr_ratio'] else "--"
            
            return (bias_text, bias_color, phase, r_high, r_eq, r_low,
                    watch, extreme, mss_text, mss_color, entry, sl, tp, rr)
    except:
        pass
    
    return ("NEUTRAL", "secondary", "--", "--", "--", "--", "--", "--", "WAITING", "secondary", "--", "--", "--", "--")


@callback(
    Output('market-structure-chart', 'figure'),
    Input('data-refresh-interval', 'n_intervals')
)
def update_market_chart(n):
    """Update market structure chart with candlesticks and structure lines."""
    try:
        from gui.utils.chart_builder import create_market_structure_chart
        return create_market_structure_chart()
    except Exception as e:
        # Return empty chart on error
        return go.Figure().update_layout(
            template='plotly_dark',
            xaxis_title="Time",
            yaxis_title="Price",
            title="Market Structure Chart"
        )


@callback(
    Output('open-positions-table', 'children'),
    Input('data-refresh-interval', 'n_intervals')
)
def update_positions_table(n):
    """Update open positions table."""
    try:
        from gui.utils.mt5_interface import get_open_positions_data
        positions = get_open_positions_data()
        
        if positions and len(positions) > 0:
            return dbc.Table.from_dataframe(
                positions,
                striped=True,
                bordered=True,
                hover=True,
                dark=True,
                size='sm'
            )
        else:
            return html.Div("No open positions", className="text-muted text-center py-3")
    except:
        return html.Div("No open positions", className="text-muted text-center py-3")


@callback(
    Output('activity-log', 'children'),
    Input('data-refresh-interval', 'n_intervals')
)
def update_activity_log(n):
    """Update recent activity log."""
    try:
        from gui.utils.mt5_interface import get_recent_activity
        activities = get_recent_activity(limit=10)
        
        if activities:
            return [
                html.Div([
                    html.Small(act['time'], className="text-muted me-2"),
                    html.Span(act['message'], className=f"text-{act['type']}")
                ], className="mb-2 pb-2 border-bottom border-dark")
                for act in activities
            ]
        else:
            return html.Div("No recent activity", className="text-muted text-center")
    except:
        return html.Div("No recent activity", className="text-muted text-center")
