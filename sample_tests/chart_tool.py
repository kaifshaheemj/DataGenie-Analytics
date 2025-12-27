from quickchart import QuickChart
from tools.data_extractor_tool import run_sql
import json

def build_chart(config_json: str):
    data = json.loads(config_json)

    qc = QuickChart()
    qc.config = data["config"]

    url = qc.get_url()

    return url

if __name__ == "__main__":
    sql_query = """SELECT
        dp.product_name,
        SUM(fs.order_quantity * dp.product_price) AS total_revenue
        FROM fact_sales fs
        JOIN dim_products dp ON fs.product_key = dp.product_key
        GROUP BY
        dp.product_name
        ORDER BY
        total_revenue DESC;"""
    question = "What are our best-selling products?"
    result = run_sql(question, sql_query)
    df = result["data"]
    print("DataFrame result:")
    print(df.head())
    chart_config = {
        "type": "bar",
        "data": {
            "labels": df["product_name"].tolist(),
            "datasets": [{
                "label": "Total Revenue",
                "data": df["total_revenue"].tolist()
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": "Best-Selling Products by Revenue"
            },
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": True
                    }
                }]
            }
        }
    }
    config_json = json.dumps({"config": chart_config})
    chart_url = build_chart(config_json)
    print("Chart URL:", chart_url)
    