"""
Trading Panel Page - Manual trading controls
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("Trading Panel", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Manual Trade Entry"),
                dbc.CardBody([
                    dbc.Label("Direction"),
                    dbc.RadioItems(
                        options=[
                            {"label": "Buy", "value": "buy"},
                            {"label": "Sell", "value": "sell"}
                        ],
                        value="buy",
                        id="trade-direction"
                    ),
                    
                    html.Hr(),
                    
                    dbc.Label("Lot Size"),
                    dbc.Input(type="number", value=0.01, step=0.01, id="trade-lots"),
                    
                    dbc.Label("Entry Price", className="mt-3"),
                    dbc.Input(type="number", id="trade-entry"),
                    
                    dbc.Label("Stop Loss", className="mt-3"),
                    dbc.Input(type="number", id="trade-sl"),
                    
                    dbc.Label("Take Profit", className="mt-3"),
                    dbc.Input(type="number", id="trade-tp"),
                    
                    html.Hr(),
                    
                    dbc.Button("Place Order", color="success", className="w-100", size="lg")
                ])
            ], className="bg-dark border-secondary")
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Current Price"),
                dbc.CardBody([
                    html.H3("Loading...", id="current-price")
                ])
            ], className="bg-dark border-secondary mb-3"),
            
            dbc.Card([
                dbc.CardHeader("Quick Actions"),
                dbc.CardBody([
                    dbc.Button("Close All Positions", color="danger", className="w-100 mb-2"),
                    dbc.Button("Cancel All Orders", color="warning", className="w-100"),
                ])
            ], className="bg-dark border-secondary")
        ], width=8)
    ])
    
], fluid=True)
