import pandas as pd
import plotly.graph_objects as go
from pmdarima import auto_arima


def run_forecast(df, time_col, value_col, horizon=6, granularity="month"):
    """
    Generic forecasting tool for business metrics.
    """

    # --------- CLEAN + VALIDATE ----------
    data = df[[time_col, value_col]].dropna().copy()

    data[time_col] = pd.to_datetime(data[time_col])
    data = data.sort_values(time_col).set_index(time_col)

    if len(data) < 15:
        raise ValueError("Not enough history to forecast. Need at least 15 points.")

    # --------- SET FREQUENCY ----------
    if granularity == "month":
        data = data.asfreq("MS").interpolate()
        seasonal = True
        m = 12

    elif granularity == "week":
        data = data.asfreq("W").interpolate()
        seasonal = True
        m = 52

    elif granularity == "quarter":
        data = data.asfreq("QS").interpolate()
        seasonal = True
        m = 4

    else:
        data = data.asfreq("D").interpolate()
        seasonal = False
        m = 1

    # --------- FIT MODEL ----------
    model = auto_arima(
        data[value_col],
        seasonal=seasonal,
        m=m,
        trace=False,
        suppress_warnings=True,
        error_action="ignore"
    )

    forecast, conf_int = model.predict(n_periods=horizon, return_conf_int=True)

    future_index = pd.date_range(start=data.index[-1], periods=horizon + 1, freq=data.index.freq)[1:]

    fc_df = pd.DataFrame({
        time_col: future_index,
        "forecast": forecast,
        "lower_bound": conf_int[:, 0],
        "upper_bound": conf_int[:, 1]
    })

    # --------- PLOT ----------
    fig = go.Figure()

    fig.add_scatter(
        x=data.index,
        y=data[value_col],
        mode="lines",
        name="History"
    )

    fig.add_scatter(
        x=future_index,
        y=forecast,
        mode="lines+markers",
        name="Forecast"
    )

    fig.add_scatter(
        x=future_index,
        y=fc_df["upper_bound"],
        fill=None,
        mode="lines",
        line_color="lightgray",
        showlegend=False
    )

    fig.add_scatter(
        x=future_index,
        y=fc_df["lower_bound"],
        fill="tonexty",
        mode="lines",
        line_color="lightgray",
        name="Confidence Interval"
    )

    fig.update_layout(
        title="Forecast",
        xaxis_title=time_col,
        yaxis_title=value_col
    )

    return fc_df, fig
