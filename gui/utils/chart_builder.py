"""
Chart Builder - Create professional trading charts with market structure
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import logging
from gui.utils.mt5_interface import get_market_data, get_trading_state

logger = logging.getLogger(__name__)


def create_market_structure_chart():
    """
    Create comprehensive market structure chart with:
    - Candlestick chart
    - Pivot highs and lows
    - Main range (high, low, EQ)
    - Minor structure levels
    - Entry setup markers
    """
    try:
        # Get market data
        df = get_market_data(timeframe='H4', count=200)
        if df is None or df.empty:
            return create_empty_chart()
        
        # Get trading state
        state = get_trading_state()
        
        # Create figure
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        ))
        
        # Add Main Range Lines (if available)
        if state:
            # Main Range High
            if state['main_range_high']:
                fig.add_hline(
                    y=state['main_range_high'],
                    line_dash="dash",
                    line_color="#00d4ff",
                    annotation_text="Main High",
                    annotation_position="right"
                )
            
            # Main Range Low
            if state['main_range_low']:
                fig.add_hline(
                    y=state['main_range_low'],
                    line_dash="dash",
                    line_color="#00d4ff",
                    annotation_text="Main Low",
                    annotation_position="right"
                )
            
            # Equilibrium (50%)
            if state['equilibrium']:
                fig.add_hline(
                    y=state['equilibrium'],
                    line_dash="dot",
                    line_color="#ffff00",
                    annotation_text="EQ (50%)",
                    annotation_position="right"
                )
            
            # Watch Pivot
            if state['watch_pivot']:
                fig.add_hline(
                    y=state['watch_pivot'],
                    line_dash="solid",
                    line_color="#ff00ff",
                    annotation_text="Watch Pivot",
                    annotation_position="right",
                    line_width=2
                )
            
            # Entry Setup (if active)
            if state['entry_price']:
                # Entry price
                fig.add_hline(
                    y=state['entry_price'],
                    line_dash="solid",
                    line_color="#00ff00",
                    annotation_text="Entry",
                    annotation_position="left",
                    line_width=2
                )
                
                # Stop Loss
                if state['stop_loss']:
                    fig.add_hline(
                        y=state['stop_loss'],
                        line_dash="solid",
                        line_color="#ff0000",
                        annotation_text="Stop Loss",
                        annotation_position="left",
                        line_width=2
                    )
                
                # Take Profit
                if state['take_profit']:
                    fig.add_hline(
                        y=state['take_profit'],
                        line_dash="solid",
                        line_color="#00ff00",
                        annotation_text="Take Profit",
                        annotation_position="left",
                        line_width=2
                    )
        
        # Update layout
        fig.update_layout(
            template='plotly_dark',
            xaxis_title="Time",
            yaxis_title="Price",
            title={
                'text': "Market Structure Analysis - 4H Timeframe",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            paper_bgcolor='#0d0d0d',
            plot_bgcolor='#1a1a1a',
            font=dict(color='#ffffff'),
            height=500
        )
        
        # Update axes
        fig.update_xaxes(
            gridcolor='#333333',
            showgrid=True,
            zeroline=False
        )
        
        fig.update_yaxes(
            gridcolor='#333333',
            showgrid=True,
            zeroline=False,
            side='right'
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating market structure chart: {e}")
        return create_empty_chart()


def create_empty_chart():
    """Create an empty chart placeholder."""
    fig = go.Figure()
    
    fig.add_annotation(
        text="No data available",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20, color="#666666")
    )
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_title="Time",
        yaxis_title="Price",
        title="Market Structure Analysis",
        paper_bgcolor='#0d0d0d',
        plot_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        height=500
    )
    
    return fig


def create_equity_curve_chart(trades_df):
    """Create equity curve chart from trade history."""
    try:
        if trades_df is None or trades_df.empty:
            return create_empty_chart()
        
        # Calculate cumulative P/L
        trades_df['cumulative_pnl'] = trades_df['profit'].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trades_df['close_time'],
            y=trades_df['cumulative_pnl'],
            mode='lines',
            name='Equity Curve',
            line=dict(color='#00d4ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.2)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            xaxis_title="Date",
            yaxis_title="Cumulative P/L ($)",
            title="Equity Curve",
            paper_bgcolor='#0d0d0d',
            plot_bgcolor='#1a1a1a',
            font=dict(color='#ffffff'),
            height=400
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating equity curve: {e}")
        return create_empty_chart()
