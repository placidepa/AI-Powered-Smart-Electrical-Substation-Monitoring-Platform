import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
import sys

# Ensure backend models can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.health_scorer import AssetHealthAssessor

# Initialize the Dash app with an industrial dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Smart Substation Analytics"

# Load the data we generated in Phase 2
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'substation_telemetry.csv')

def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.tail(300) # Load the last 300 points for the "live" view
    else:
        return pd.DataFrame()

df = load_data()
health_assessor = AssetHealthAssessor()

# Calculate current health based on the latest reading
if not df.empty:
    latest = df.iloc[-1]
    current_health = health_assessor.calculate_health_score(latest['transformer_temp_c'], latest['current_a'])
    rul_days = health_assessor.estimate_rul(current_health)
    active_anomalies = len(df[df['label'] != 0])
else:
    current_health, rul_days, active_anomalies = 100.0, 1000, 0

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H2("⚡ AI Smart Substation Monitoring Platform", className="text-center mt-4 mb-4 text-info"))
    ]),
    
    # KPI Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Transformer T1 - Health Score"),
            dbc.CardBody(html.H3(f"{current_health:.1f} / 100", className="text-success text-center" if current_health > 70 else "text-danger text-center"))
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Active Anomalies (Last 24h)"),
            dbc.CardBody(html.H3(f"{active_anomalies}", className="text-warning text-center" if active_anomalies > 0 else "text-info text-center"))
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Est. Remaining Useful Life"),
            dbc.CardBody(html.H3(f"{rul_days} Days", className="text-success text-center" if rul_days > 500 else "text-danger text-center"))
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("System Status"),
            dbc.CardBody(html.H3("CRITICAL" if active_anomalies > 5 else "STABLE", className="text-danger text-center" if active_anomalies > 5 else "text-success text-center"))
        ]), width=3),
    ], className="mb-4"),
    
    # Telemetry Graph
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Real-Time Telemetry (Voltage & Current)"),
            dbc.CardBody([
                dcc.Graph(id='telemetry-graph'),
                dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0) # Refreshes every 5 seconds
            ])
        ]), width=12)
    ])
], fluid=True)

@app.callback(
    Output('telemetry-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    # In a production app, this would query the database/Redis. 
    # We will just reload our static dataframe for demonstration.
    live_df = load_data()
    
    fig = go.Figure()
    if not live_df.empty:
        fig.add_trace(go.Scatter(x=live_df['timestamp'], y=live_df['voltage_kv'], name='Voltage (kV)', line=dict(color='#00FFFF', width=2)))
        # Scale current down so it fits nicely on the same Y-axis as voltage
        fig.add_trace(go.Scatter(x=live_df['timestamp'], y=live_df['current_a']/4, name='Current (A/4 scaled)', line=dict(color='#FFD700', width=2)))
        
        # Highlight anomalies in red
        anomalies = live_df[live_df['label'] != 0]
        fig.add_trace(go.Scatter(x=anomalies['timestamp'], y=anomalies['voltage_kv'], mode='markers', name='Anomaly Detected', marker=dict(color='red', size=8, symbol='x')))

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

if __name__ == '__main__':
    print("[INFO] Starting Substation Dashboard on http://127.0.0.1:8050/")
    app.run_server(debug=True, port=8050)