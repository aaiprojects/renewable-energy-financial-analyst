"""
Dynamic Chart Generator for Renewable Energy Financial Analysis
Creates interactive visualizations based on query requirements.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime, timedelta

from ..tools.prices import PricesTool
from ..tools.metadata import MetadataTool
from ..config.watchlist import WATCHLIST

class ChartGenerator:
    def __init__(self):
        self.prices_tool = PricesTool()
        self.metadata_tool = MetadataTool()
        
        # Color scheme for renewable energy sectors
        self.sector_colors = {
            'Solar': '#FFA500',      # Orange
            'Wind': '#87CEEB',       # Sky Blue  
            'Utility': '#32CD32',    # Lime Green
            'Storage': '#8A2BE2',    # Blue Violet
            'Other': '#696969'       # Dim Gray
        }

    def create_price_chart(self, tickers: List[str], timeframe: str = "30d", 
                          chart_type: str = "line") -> go.Figure:
        """Create price performance chart for specified tickers."""
        if not tickers:
            return self._create_empty_chart("No tickers specified")
        
        days = self._parse_timeframe(timeframe)
        fig = go.Figure()
        
        for ticker in tickers:
            try:
                df = self.prices_tool.fetch_history(ticker, days)
                if df is not None and not df.empty:
                    # Get company metadata for better labeling
                    meta = self.metadata_tool.get_metadata(ticker)
                    company_name = meta.long_name or ticker
                    
                    if chart_type == "candlestick":
                        fig.add_trace(go.Candlestick(
                            x=df['Date'],
                            open=df['Open'],
                            high=df['High'], 
                            low=df['Low'],
                            close=df['Close'],
                            name=f"{ticker} ({company_name})"
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=df['Date'],
                            y=df['Close'],
                            mode='lines',
                            name=f"{ticker} ({company_name})",
                            line=dict(width=2)
                        ))
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        
        fig.update_layout(
            title=f"Price Performance - {', '.join(tickers)} ({timeframe})",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig

    def create_comparison_chart(self, tickers: List[str], metrics: List[str], 
                              timeframe: str = "30d") -> go.Figure:
        """Create comparison chart across multiple metrics."""
        if not tickers:
            return self._create_empty_chart("No tickers specified")
        
        days = self._parse_timeframe(timeframe)
        
        # If no specific metrics, default to returns comparison
        if not metrics or 'returns' in metrics:
            return self._create_returns_comparison(tickers, days)
        elif 'volatility' in metrics:
            return self._create_volatility_comparison(tickers, days)
        else:
            return self._create_returns_comparison(tickers, days)

    def create_sector_overview(self, subsector: Optional[str] = None) -> go.Figure:
        """Create sector overview visualization."""
        # Filter watchlist by subsector if specified
        if subsector:
            filtered_watchlist = [w for w in WATCHLIST if w.subsector.lower() == subsector.lower()]
        else:
            filtered_watchlist = WATCHLIST
        
        if not filtered_watchlist:
            return self._create_empty_chart(f"No companies found for subsector: {subsector}")
        
        tickers = [w.ticker for w in filtered_watchlist]
        
        # Get recent performance data
        quote_data = self.prices_tool.batch_quotes(tickers)
        if quote_data is None or quote_data.empty:
            return self._create_empty_chart("Unable to fetch market data")
        
        # Merge with company metadata
        company_data = []
        for w in filtered_watchlist:
            company_data.append({
                'ticker': w.ticker,
                'name': w.name,
                'subsector': w.subsector,
                'region': w.region
            })
        
        df = pd.DataFrame(company_data)
        df = df.merge(quote_data, on='ticker', how='left')
        
        # Create bubble chart: x=price, y=change%, size=market_cap (simulated)
        fig = px.scatter(
            df,
            x='price',
            y='pct_change',
            size='price',  # Using price as proxy for size
            color='subsector',
            hover_data=['name', 'ticker'],
            title=f"Renewable Energy Sector Overview{' - ' + subsector if subsector else ''}",
            labels={
                'price': 'Current Price ($)',
                'pct_change': 'Daily Change (%)',
                'subsector': 'Subsector'
            },
            color_discrete_map=self.sector_colors
        )
        
        fig.update_layout(
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig

    def create_technical_analysis_chart(self, ticker: str, timeframe: str = "30d") -> go.Figure:
        """Create technical analysis chart with indicators."""
        days = self._parse_timeframe(timeframe)
        
        try:
            df = self.prices_tool.fetch_history(ticker, days)
            if df is None or df.empty:
                return self._create_empty_chart(f"No data available for {ticker}")
            
            # Calculate technical indicators
            df = self._add_technical_indicators(df)
            
            # Create subplot figure
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{ticker} Price & Moving Averages', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # Price and moving averages
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['Close'],
                mode='lines', name='Price',
                line=dict(color='black', width=2)
            ), row=1, col=1)
            
            if 'MA20' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['Date'], y=df['MA20'],
                    mode='lines', name='MA20',
                    line=dict(color='blue', width=1)
                ), row=1, col=1)
            
            if 'MA50' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['Date'], y=df['MA50'],
                    mode='lines', name='MA50',
                    line=dict(color='red', width=1)
                ), row=1, col=1)
            
            # Volume
            fig.add_trace(go.Bar(
                x=df['Date'], y=df['Volume'],
                name='Volume',
                marker_color='lightblue'
            ), row=2, col=1)
            
            fig.update_layout(
                title=f"Technical Analysis - {ticker}",
                template='plotly_white',
                height=600,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            return self._create_empty_chart(f"Error creating technical analysis for {ticker}: {str(e)}")

    def _create_returns_comparison(self, tickers: List[str], days: int) -> go.Figure:
        """Create returns comparison chart."""
        returns_data = []
        
        for ticker in tickers:
            try:
                df = self.prices_tool.fetch_history(ticker, days + 5)  # Extra days for calculation
                if df is not None and not df.empty and len(df) > 1:
                    start_price = df['Close'].iloc[0]
                    end_price = df['Close'].iloc[-1]
                    total_return = ((end_price - start_price) / start_price) * 100
                    
                    # Get company name
                    meta = self.metadata_tool.get_metadata(ticker)
                    company_name = meta.long_name or ticker
                    
                    returns_data.append({
                        'ticker': ticker,
                        'company': company_name,
                        'return': total_return
                    })
            except Exception as e:
                print(f"Error calculating returns for {ticker}: {e}")
        
        if not returns_data:
            return self._create_empty_chart("Unable to calculate returns")
        
        df_returns = pd.DataFrame(returns_data)
        df_returns = df_returns.sort_values('return', ascending=True)
        
        # Color bars based on positive/negative returns
        colors = ['red' if x < 0 else 'green' for x in df_returns['return']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=df_returns['return'],
                y=df_returns['ticker'],
                orientation='h',
                marker_color=colors,
                text=[f"{r:.1f}%" for r in df_returns['return']],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Returns Comparison ({days} days)",
            xaxis_title="Return (%)",
            yaxis_title="Companies",
            template='plotly_white',
            height=400
        )
        
        return fig

    def _create_volatility_comparison(self, tickers: List[str], days: int) -> go.Figure:
        """Create volatility comparison chart."""
        volatility_data = []
        
        for ticker in tickers:
            try:
                df = self.prices_tool.fetch_history(ticker, days)
                if df is not None and not df.empty and len(df) > 1:
                    # Calculate daily returns
                    df['daily_return'] = df['Close'].pct_change()
                    volatility = df['daily_return'].std() * np.sqrt(252) * 100  # Annualized volatility
                    
                    # Get company name
                    meta = self.metadata_tool.get_metadata(ticker)
                    company_name = meta.long_name or ticker
                    
                    volatility_data.append({
                        'ticker': ticker,
                        'company': company_name,
                        'volatility': volatility
                    })
            except Exception as e:
                print(f"Error calculating volatility for {ticker}: {e}")
        
        if not volatility_data:
            return self._create_empty_chart("Unable to calculate volatility")
        
        df_vol = pd.DataFrame(volatility_data)
        df_vol = df_vol.sort_values('volatility', ascending=True)
        
        fig = go.Figure(data=[
            go.Bar(
                x=df_vol['volatility'],
                y=df_vol['ticker'],
                orientation='h',
                marker_color='purple',
                text=[f"{v:.1f}%" for v in df_vol['volatility']],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Volatility Comparison (Annualized) - {days} days",
            xaxis_title="Volatility (%)",
            yaxis_title="Companies",
            template='plotly_white',
            height=400
        )
        
        return fig

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to price data."""
        # Moving averages
        if len(df) >= 20:
            df['MA20'] = df['Close'].rolling(window=20).mean()
        if len(df) >= 50:
            df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI (simplified)
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        return df

    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to number of days."""
        timeframe_map = {
            '1d': 1, '7d': 7, '30d': 30, '90d': 90, '365d': 365, 'ytd': 250
        }
        return timeframe_map.get(timeframe, 30)

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with error message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Chart Generation Error",
            template='plotly_white',
            height=400
        )
        return fig