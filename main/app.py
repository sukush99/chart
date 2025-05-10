from fastapi import FastAPI, Response, Query
import pandas as pd
import plotly.graph_objects as go

app = FastAPI()

TA_COLUMNS = [
    'ADJ_EMA_50',
    'ADJ_SMA_50', 
    'ADJ_VWAP'
]

COLOR_MAP = {

    'ADJ_EMA_50': 'purple',
    'ADJ_SMA_50': 'brown',
    'ADJ_VWAP': 'pink',

}

@app.get("/chart/{symbol}")
def chart(symbol: str, ta: bool = Query(False, description="Include technical indicators")):
    df = pd.read_csv("data/stock_data.csv")
    df = df[df["symbol"] == symbol].copy()

    if df.empty:
        return Response(content=f"No data for symbol: {symbol}", media_type="text/plain", status_code=404)

    # If TA requested, merge with TA data
    if ta:
        try:
            ta_df = pd.read_csv("data/stock_data_ta.csv", usecols=["symbol", "date"] + TA_COLUMNS)
            ta_df = ta_df[ta_df["symbol"] == symbol].copy()
            df = pd.merge(df, ta_df, on=["symbol", "date"], how="left")
        except Exception as e:
            return Response(content=f"TA load error: {e}", media_type="text/plain", status_code=500)

    fig = go.Figure()

    # Main candlestick
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        line=dict(width=1),
        whiskerwidth=0.6,
        name=symbol.upper()
    ))

    # Add indicators if enabled
    if ta:
        for col in TA_COLUMNS:
            if col in df.columns and df[col].notna().any():
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df[col],
                    mode='lines',
                    name=col,
                    line=dict(width=1.5, dash='dot', color=COLOR_MAP.get(col, 'black'))
                ))

    fig.update_layout(
        title={
            'text': f"{symbol.upper()} Candlestick Chart{' with Indicators' if ta else ''}",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=24, color='black')
        },
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        xaxis_rangeslider_visible=True,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label='1W', step='day', stepmode='backward'),
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(step='all')
                ])
            ),
            type='date',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(fixedrange=False, showgrid=True, gridcolor='lightgray'),
        font=dict(family="Segoe UI, Roboto, Arial", size=14, color='black'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40),
        autosize=True
    )


    fig.update_traces(showlegend=True)

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return Response(content=html_str, media_type="text/html")
