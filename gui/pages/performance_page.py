"""
Performance Page - Trading analytics and statistics
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("Performance Analytics", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("75.0%", className="mb-0 text-success"),
                    html.Small("Win Rate", className="text-muted")
                ])
            ], className="text-center bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("2.5", className="mb-0 text-info"),
                    html.Small("Avg R:R", className="text-muted")
                ])
            ], className="text-center bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("$1,250", className="mb-0 text-success"),
                    html.Small("Total Profit", className="text-muted")
                ])
            ], className="text-center bg-dark border-secondary")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("24", className="mb-0 text-warning"),
                    html.Small("Total Trades", className="text-muted")
                ])
            ], className="text-center bg-dark border-secondary")
        ], width=3),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Equity Curve"),
                dbc.CardBody([
                    dcc.Graph(id='equity-curve', style={'height': '400px'})
                ])
            ], className="bg-dark border-secondary")
        ])
    ])
    
], fluid=True)
