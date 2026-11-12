"""
Symbols Page - Multi-Symbol Configuration and Management
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
from symbol_manager import get_symbol_manager
import logging

logger = logging.getLogger(__name__)

# Page Layout
layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2([
                html.I(className="fas fa-layer-group me-3"),
                "Trading Symbols Management"
            ], className="mb-0"),
            html.P("Manage multiple trading pairs with individual configurations", className="text-muted mb-0")
        ])
    ], className="mb-4 pb-3 border-bottom border-secondary"),
    
    # Alert
    dbc.Row([
        dbc.Col([
            html.Div(id='symbols-alert')
        ])
    ], className="mb-3"),
    
    # Add New Symbol Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-plus-circle me-2"),
                    "Add New Trading Symbol"
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Symbol"),
                            dbc.Input(
                                id="input-new-symbol",
                                type="text",
                                placeholder="e.g., EURUSD, GBPUSD",
                                style={"textTransform": "uppercase"}
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Main Timeframe"),
                            dbc.Select(
                                id="select-new-main-tf",
                                options=[
                                    {"label": "15 Minutes", "value": "M15"},
                                    {"label": "30 Minutes", "value": "M30"},
                                    {"label": "1 Hour", "value": "H1"},
                                    {"label": "4 Hours", "value": "H4"},
                                    {"label": "Daily", "value": "D1"},
                                ],
                                value="H4"
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Minor Timeframe"),
                            dbc.Select(
                                id="select-new-minor-tf",
                                options=[
                                    {"label": "5 Minutes", "value": "M5"},
                                    {"label": "15 Minutes", "value": "M15"},
                                    {"label": "30 Minutes", "value": "M30"},
                                    {"label": "1 Hour", "value": "H1"},
                                ],
                                value="H1"
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Action", className="d-block"),
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Add Symbol"
                            ], id="btn-add-symbol", color="success", className="mt-0")
                        ], width=3),
                    ])
                ])
            ], className="bg-dark border-secondary mb-4")
        ])
    ]),
    
    # Active Symbols List
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-list me-2"),
                    "Active Trading Symbols"
                ]),
                dbc.CardBody([
                    html.Div(id='symbols-table-container')
                ])
            ], className="bg-dark border-secondary")
        ])
    ]),
    
], fluid=True)


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    [Output('symbols-alert', 'children'),
     Output('input-new-symbol', 'value')],
    Input('btn-add-symbol', 'n_clicks'),
    [State('input-new-symbol', 'value'),
     State('select-new-main-tf', 'value'),
     State('select-new-minor-tf', 'value')],
    prevent_initial_call=True
)
def add_new_symbol(n_clicks, symbol, main_tf, minor_tf):
    """Add a new trading symbol."""
    if not symbol or len(symbol.strip()) == 0:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please enter a valid symbol"
        ], color="warning", dismissable=True)
        return alert, symbol
    
    symbol = symbol.strip().upper()
    
    try:
        manager = get_symbol_manager()
        success = manager.add_symbol(symbol, main_tf=main_tf, minor_tf=minor_tf, enabled=True)
        
        if success:
            alert = dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Symbol {symbol} added successfully!"
            ], color="success", dismissable=True, duration=4000)
            return alert, ""  # Clear input
        else:
            alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Symbol {symbol} already exists"
            ], color="warning", dismissable=True)
            return alert, symbol
    
    except Exception as e:
        logger.error(f"Error adding symbol: {e}")
        alert = dbc.Alert([
            html.I(className="fas fa-times-circle me-2"),
            f"Error: {str(e)}"
        ], color="danger", dismissable=True)
        return alert, symbol


@callback(
    Output('symbols-table-container', 'children'),
    Input('data-refresh-interval', 'n_intervals')
)
def update_symbols_table(n):
    """Update the symbols table with current status."""
    try:
        manager = get_symbol_manager()
        summaries = manager.get_all_symbols_summary()
        
        if not summaries:
            return html.Div("No symbols configured", className="text-muted text-center py-3")
        
        # Create table rows
        rows = []
        for summary in summaries:
            status_color = "success" if summary['enabled'] else "secondary"
            bias_color = "success" if summary['bias'] == "BULLISH" else "danger" if summary['bias'] == "BEARISH" else "secondary"
            
            row = html.Tr([
                html.Td([
                    html.Strong(summary['symbol']),
                    html.Br(),
                    dbc.Badge("Active" if summary['enabled'] else "Inactive", color=status_color, className="mt-1")
                ]),
                html.Td(f"{summary['main_timeframe']}"),
                html.Td(f"{summary['minor_timeframe']}"),
                html.Td([
                    dbc.Badge(summary['bias'], color=bias_color)
                ]),
                html.Td(summary['phase'].replace('_', ' ').title(), style={'fontSize': '0.85em'}),
                html.Td([
                    html.I(className="fas fa-check-circle text-success" if summary['main_range_valid'] else "fas fa-times-circle text-muted")
                ], className="text-center"),
                html.Td([
                    html.I(className="fas fa-check-circle text-success" if summary['minor_mss_confirmed'] else "fas fa-times-circle text-muted")
                ], className="text-center"),
                html.Td([
                    html.I(className="fas fa-check-circle text-success" if summary['position_open'] else "fas fa-minus-circle text-muted")
                ], className="text-center"),
                html.Td([
                    dbc.ButtonGroup([
                        dbc.Button(
                            html.I(className="fas fa-eye"),
                            id={'type': 'btn-view-symbol', 'index': summary['symbol']},
                            color="info",
                            size="sm",
                            title="View Details"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-edit"),
                            id={'type': 'btn-edit-symbol', 'index': summary['symbol']},
                            color="warning",
                            size="sm",
                            title="Edit Settings"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-trash"),
                            id={'type': 'btn-delete-symbol', 'index': summary['symbol']},
                            color="danger",
                            size="sm",
                            title="Remove"
                        ),
                    ], size="sm")
                ], className="text-center"),
            ])
            rows.append(row)
        
        # Create table
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Symbol"),
                    html.Th("Main TF"),
                    html.Th("Minor TF"),
                    html.Th("Bias"),
                    html.Th("Phase"),
                    html.Th("Range", className="text-center"),
                    html.Th("MSS", className="text-center"),
                    html.Th("Position", className="text-center"),
                    html.Th("Actions", className="text-center"),
                ])
            ]),
            html.Tbody(rows)
        ], bordered=True, hover=True, striped=True, dark=True, size='sm', responsive=True)
        
        return table
    
    except Exception as e:
        logger.error(f"Error updating symbols table: {e}")
        return html.Div("Error loading symbols", className="text-danger text-center")
