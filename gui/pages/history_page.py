"""
Trade History Page - Complete trading history and analytics
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("Trade History", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filter Trades"),
                dbc.CardBody([
                    dbc.Label("Date Range"),
                    dcc.DatePickerRange(id='date-range'),
                    
                    dbc.Label("Trade Type", className="mt-3"),
                    dbc.Select(
                        options=[
                            {"label": "All", "value": "all"},
                            {"label": "Buy Only", "value": "buy"},
                            {"label": "Sell Only", "value": "sell"}
                        ],
                        value="all"
                    )
                ])
            ], className="bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Trade History Table"),
                dbc.CardBody([
                    html.Div("No trades found", className="text-muted text-center")
                ])
            ], className="bg-dark border-secondary")
        ], width=9)
    ])
    
], fluid=True)
