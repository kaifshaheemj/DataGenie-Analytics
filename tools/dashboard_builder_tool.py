import os

def build_dashboard_from_paths(
    chart_paths,
    output_path="C:\\DataGenie\\DataGenie-Analytics\\DASHBOARD.html"
):
    """
    Build one dashboard HTML from a list of saved chart file paths.
    """

    if not chart_paths:
        print("No charts provided — dashboard NOT created.")
        return None

    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    html = """
    <html>
    <head>
        <title>AdventureWorks Dashboard</title>
        <style>
            body { font-family: Arial; background: #f7f7f7; }
            h1 { text-align:center; }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                padding: 20px;
            }
            img {
                width: 100%;
                height: 450px;
                object-fit: contain;
                border: 1px solid #ccc;
                border-radius: 10px;
                background: white;
                padding: 10px;
            }
        </style>
    </head>
    <body>
        <h1>📊 AdventureWorks Executive Dashboard</h1>
        <div class="grid">
    """

    for path in chart_paths:
        rel = os.path.relpath(path, os.path.dirname(output_path))

        html += f"""
        <a href="{rel}" target="_blank">
            <img src="{rel}" />
        </a>
        """


    html += """
        </div>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Dashboard created:", output_path)
    return output_path


if __name__ == "__main__":
    paths = [
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\total_revenue_by_product_bar_14-16-17.png",
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\quarterly_revenue_trend_over_two_years_line_14-14-44.png",
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\top_product_category_subcategory_combinations_by_profit_bar_14-15-14.png",
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\country_profit_margins_vs_company_average_bar_14-15-40.png",
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\product_return_rate_by_category_bar_14-15-50.png",
        "C:\\DataGenie\\DataGenie-Analytics\\visualizations\\2025-12-27\\products_by_profit_margin_percentage_bar_14-16-07.png"
    ]

    build_dashboard_from_paths(paths)
