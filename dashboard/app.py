import os
import sys

import dash
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# Ensure backend models can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models.health_scorer import AssetHealthAssessor


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Smart Substation Analytics"

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "substation_telemetry.csv"
)
FEATURE_COLUMNS = [
    "timestamp",
    "voltage_kv",
    "current_a",
    "frequency_hz",
    "transformer_temp_c",
    "oil_temp_c",
    "power_factor",
    "breaker_status",
    "label",
]
FAULT_OPTIONS = {
    0: "Normal",
    1: "Overload",
    2: "Short Circuit",
    3: "Cooling Failure",
}

health_assessor = AssetHealthAssessor()


def load_initial_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)
        return df[FEATURE_COLUMNS].tail(120).to_dict("records")

    now = pd.Timestamp.now()
    records = []
    for i in range(120, 0, -1):
        records.append(
            make_reading(
                timestamp=now - pd.Timedelta(seconds=i),
                voltage_kv=110,
                current_a=420,
                transformer_temp_c=62,
                oil_temp_c=52,
                power_factor=0.97,
                fault_label=0,
            )
        )
    return records


def infer_fault_label(voltage_kv, current_a, transformer_temp_c, oil_temp_c):
    if voltage_kv < 80 and current_a > 1000:
        return 2
    if transformer_temp_c > 95 and oil_temp_c > 75:
        return 3
    if current_a > 700 or transformer_temp_c > 85:
        return 1
    return 0


def apply_fault_signature(voltage_kv, current_a, transformer_temp_c, oil_temp_c, fault_label):
    if fault_label == 1:
        return voltage_kv * 0.98, current_a * 1.55, transformer_temp_c + 15, oil_temp_c + 8
    if fault_label == 2:
        return voltage_kv * 0.55, current_a * 4.0, transformer_temp_c + 5, oil_temp_c + 3
    if fault_label == 3:
        return voltage_kv, current_a * 1.05, transformer_temp_c + 30, oil_temp_c + 25
    return voltage_kv, current_a, transformer_temp_c, oil_temp_c


def make_reading(
    timestamp,
    voltage_kv,
    current_a,
    transformer_temp_c,
    oil_temp_c,
    power_factor,
    fault_label=0,
):
    breaker_status = 0 if fault_label == 2 else 1
    return {
        "timestamp": pd.Timestamp(timestamp).isoformat(),
        "voltage_kv": round(float(voltage_kv), 2),
        "current_a": round(float(current_a), 2),
        "frequency_hz": round(float(np.random.normal(50.0, 0.015)), 3),
        "transformer_temp_c": round(float(transformer_temp_c), 1),
        "oil_temp_c": round(float(oil_temp_c), 1),
        "power_factor": round(float(power_factor), 3),
        "breaker_status": breaker_status,
        "label": int(fault_label),
    }


def status_for(health, active_anomalies, latest_label):
    if latest_label == 2 or health < 35:
        return "CRITICAL", "text-danger text-center"
    if latest_label != 0 or active_anomalies > 0 or health < 70:
        return "WARNING", "text-warning text-center"
    return "STABLE", "text-success text-center"


def metric_card(title, value_id, class_name="text-info text-center"):
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(title),
                dbc.CardBody(html.H3(id=value_id, className=class_name)),
            ]
        ),
        width=3,
    )


app.layout = dbc.Container(
    [
        dcc.Store(id="telemetry-store", data=load_initial_data()),
        dbc.Row(
            [
                dbc.Col(
                    html.H2(
                        "AI Smart Substation Monitoring Platform",
                        className="text-center mt-4 mb-4 text-info",
                    )
                )
            ]
        ),
        dbc.Row(
            [
                metric_card("Transformer T1 - Health Score", "health-score"),
                metric_card("Active Anomalies", "active-anomalies"),
                metric_card("Est. Remaining Useful Life", "rul-days"),
                metric_card("System Status", "system-status"),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Operator Input"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Voltage kV"),
                                                    dcc.Slider(
                                                        id="voltage-input",
                                                        min=50,
                                                        max=125,
                                                        step=1,
                                                        value=110,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": True},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Current A"),
                                                    dcc.Slider(
                                                        id="current-input",
                                                        min=100,
                                                        max=1200,
                                                        step=10,
                                                        value=420,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": True},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Transformer Temp C"),
                                                    dcc.Slider(
                                                        id="temp-input",
                                                        min=30,
                                                        max=130,
                                                        step=1,
                                                        value=62,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": True},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Oil Temp C"),
                                                    dcc.Slider(
                                                        id="oil-temp-input",
                                                        min=25,
                                                        max=115,
                                                        step=1,
                                                        value=52,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": True},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Power Factor"),
                                                    dcc.Slider(
                                                        id="power-factor-input",
                                                        min=0.75,
                                                        max=1.0,
                                                        step=0.005,
                                                        value=0.97,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": True},
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Fault Scenario"),
                                                    dcc.Dropdown(
                                                        id="fault-input",
                                                        options=[
                                                            {"label": name, "value": value}
                                                            for value, name in FAULT_OPTIONS.items()
                                                        ],
                                                        value=0,
                                                        clearable=False,
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Live Mode"),
                                                    dbc.Checklist(
                                                        id="stream-toggle",
                                                        options=[{"label": "Stream", "value": "on"}],
                                                        value=["on"],
                                                        switch=True,
                                                    ),
                                                    dbc.Button(
                                                        "Inject Fault",
                                                        id="inject-fault",
                                                        color="danger",
                                                        className="mt-2 w-100",
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Real-Time Telemetry"),
                            dbc.CardBody(
                                [
                                    dcc.Graph(id="telemetry-graph"),
                                    dcc.Interval(
                                        id="interval-component",
                                        interval=1000,
                                        n_intervals=0,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    width=12,
                )
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("telemetry-store", "data"),
    Input("interval-component", "n_intervals"),
    Input("inject-fault", "n_clicks"),
    State("telemetry-store", "data"),
    State("voltage-input", "value"),
    State("current-input", "value"),
    State("temp-input", "value"),
    State("oil-temp-input", "value"),
    State("power-factor-input", "value"),
    State("fault-input", "value"),
    State("stream-toggle", "value"),
)
def update_telemetry_store(
    _n_intervals,
    _n_clicks,
    records,
    voltage_kv,
    current_a,
    transformer_temp_c,
    oil_temp_c,
    power_factor,
    fault_label,
    stream_toggle,
):
    trigger = dash.ctx.triggered_id
    stream_enabled = "on" in (stream_toggle or [])

    if trigger == "interval-component" and not stream_enabled:
        return records

    records = records or []
    selected_fault = int(fault_label or 0) if trigger == "inject-fault" else 0

    voltage_kv += float(np.random.normal(0, 0.25))
    current_a += float(np.random.normal(0, 8))
    transformer_temp_c += float(np.random.normal(0, 0.5))
    oil_temp_c += float(np.random.normal(0, 0.4))

    if selected_fault:
        voltage_kv, current_a, transformer_temp_c, oil_temp_c = apply_fault_signature(
            voltage_kv,
            current_a,
            transformer_temp_c,
            oil_temp_c,
            selected_fault,
        )
        label = selected_fault
    else:
        label = infer_fault_label(voltage_kv, current_a, transformer_temp_c, oil_temp_c)

    records.append(
        make_reading(
            timestamp=pd.Timestamp.now(),
            voltage_kv=voltage_kv,
            current_a=current_a,
            transformer_temp_c=transformer_temp_c,
            oil_temp_c=oil_temp_c,
            power_factor=power_factor,
            fault_label=label,
        )
    )
    return records[-300:]


@app.callback(
    Output("telemetry-graph", "figure"),
    Output("health-score", "children"),
    Output("health-score", "className"),
    Output("active-anomalies", "children"),
    Output("active-anomalies", "className"),
    Output("rul-days", "children"),
    Output("rul-days", "className"),
    Output("system-status", "children"),
    Output("system-status", "className"),
    Input("telemetry-store", "data"),
)
def update_dashboard(records):
    live_df = pd.DataFrame(records or [], columns=FEATURE_COLUMNS)
    fig = go.Figure()

    if live_df.empty:
        return fig, "100.0 / 100", "text-success text-center", "0", "text-info text-center", "1400.0 Days", "text-success text-center", "STABLE", "text-success text-center"

    latest = live_df.iloc[-1]
    health = float(
        health_assessor.calculate_health_score(
            latest["transformer_temp_c"], latest["current_a"]
        )
    )
    rul = float(health_assessor.estimate_rul(health))
    active_anomalies = int((live_df.tail(120)["label"] != 0).sum())
    status_text, status_class = status_for(health, active_anomalies, int(latest["label"]))

    fig.add_trace(
        go.Scatter(
            x=live_df["timestamp"],
            y=live_df["voltage_kv"],
            name="Voltage (kV)",
            line=dict(color="#00FFFF", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=live_df["timestamp"],
            y=live_df["current_a"] / 4,
            name="Current (A/4 scaled)",
            line=dict(color="#FFD700", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=live_df["timestamp"],
            y=live_df["transformer_temp_c"],
            name="Transformer Temp (C)",
            line=dict(color="#FF7F50", width=2),
        )
    )

    anomalies = live_df[live_df["label"] != 0]
    fig.add_trace(
        go.Scatter(
            x=anomalies["timestamp"],
            y=anomalies["voltage_kv"],
            mode="markers",
            name="Anomaly",
            marker=dict(color="red", size=9, symbol="x"),
            text=[FAULT_OPTIONS.get(int(label), "Unknown") for label in anomalies["label"]],
            hovertemplate="%{x}<br>%{text}<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        uirevision="live-stream",
    )

    health_class = "text-success text-center" if health > 70 else "text-danger text-center"
    anomaly_class = "text-warning text-center" if active_anomalies else "text-info text-center"
    rul_class = "text-success text-center" if rul > 500 else "text-danger text-center"

    return (
        fig,
        f"{health:.1f} / 100",
        health_class,
        str(active_anomalies),
        anomaly_class,
        f"{rul:.1f} Days",
        rul_class,
        status_text,
        status_class,
    )


if __name__ == "__main__":
    print("[INFO] Starting Substation Dashboard on http://127.0.0.1:8050/")
    app.run(debug=False, port=8050)
