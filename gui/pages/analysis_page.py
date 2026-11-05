"""
Live Analysis Page - Detailed multi-timeframe analysis
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("Live Market Analysis", className="mb-4"),
    html.P("Multi-timeframe market structure analysis in real-time."),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("HTF - 4H Chart"),
                dbc.CardBody([
                    dcc.Graph(id='chart-htf', style={'height': '400px'})
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Minor - 1H Chart"),
                dbc.CardBody([
                    dcc.Graph(id='chart-minor', style={'height': '400px'})
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Entry - 15m Chart"),
                dbc.CardBody([
                    dcc.Graph(id='chart-entry', style={'height': '400px'})
                ])
            ], className="bg-dark border-secondary")
        ])
    ])
    
], fluid=True)
