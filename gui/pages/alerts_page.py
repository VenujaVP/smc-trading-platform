"""
Alerts Page - Trading alerts and notifications
"""

from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("Alerts & Notifications", className="mb-4"),
    
    dbc.Card([
        dbc.CardHeader("Recent Alerts"),
        dbc.CardBody([
            html.Div([
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "System initialized successfully"
                ], color="info", dismissable=True),
                
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "MT5 connection established"
                ], color="success", dismissable=True),
            ])
        ])
    ], className="bg-dark border-secondary")
    
], fluid=True)
