import re
import pandas as pd
import plotly.express as px
from typing import Optional


def build_chart_from_result(response: str, df: pd.DataFrame) -> Optional[object]:
    """
    If the agent's response contains a CHART: directive, parse it and
    return a Plotly figure. Otherwise return None.

    Expected format in response:
        CHART: bar | x=product | y=revenue
        CHART: line | x=date | y=sales
        CHART: scatter | x=price | y=quantity
    """
    match = re.search(
        r"CHART:\s*(\w+)\s*\|\s*x=(\w[\w\s]*)\s*\|\s*y=(\w[\w\s]*)",
        response,
        re.IGNORECASE,
    )
    if not match:
        return None

    chart_type = match.group(1).strip().lower()
    x_col = match.group(2).strip()
    y_col = match.group(3).strip()

    # Validate columns exist
    if x_col not in df.columns or y_col not in df.columns:
        return None

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        else:
            return None

        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=400,
        )
        return fig

    except Exception:
        return None


def maybe_render_chart(response: str, df: pd.DataFrame) -> Optional[object]:
    """Alias kept for import compatibility."""
    return build_chart_from_result(response, df)
