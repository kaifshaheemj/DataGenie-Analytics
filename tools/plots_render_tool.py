import json
import plotly.express as px
import os
from datetime import datetime
from utils.file_utils import slugify
from utils.clean_utils import clean_json

BASE_DIR = "visualizations"

def render_plotly(df, spec_json):
    print("\nRAW VISUAL SPEC:", repr(spec_json))
    spec = json.loads(clean_json(spec_json))
    print("CLEANED VISUAL SPEC:", spec)
    chart_type = spec["chart_type"]
    x = spec["x"]
    y = spec["y"]
    title = spec["title"]
    print(f"Rendering {chart_type} chart: {title} (x: {x}, y: {y})")

    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title)

    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title)

    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)

    else:
        fig = px.scatter(df, x=x, y=y, title=title)

    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H-%M-%S")

    folder = os.path.join(BASE_DIR, today)
    os.makedirs(folder, exist_ok=True)

    filename = f"{slugify(title)}_{chart_type}_{time_str}.html"
    full_path = os.path.join(folder, filename)

    # ---------------------
    # save chart
    # ---------------------
    fig.write_html(full_path)

    print(f"Chart saved to: {full_path}")

    return full_path, fig
