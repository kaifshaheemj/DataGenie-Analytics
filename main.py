import json
from graph.agent_graph import agents_graph
from save_results import append_result_to_csv
from tools.data_extractor_tool import run_sql
from tools.plots_render_tool import render_plotly
from tools.dashboard_builder_tool import build_dashboard
from utils.clean_utils import clean_json

from agents.sql_feedback_agent import run_sql_feedback_agent
from agents.visualization_agent import run_visualization_agent
from agents.dashboard_agent import run_dashboard_agent

if __name__ == "__main__":
    print("Hello from main.py")

    questions = [
        "Give me an overall business performance dashboard",
        "Which products have the highest profit margin?",
        "What are our best-selling products?",
        "What is the total sales for last quarter?"
    ]

    for question in questions:

        print("\n\nQuestion:", question)
        result = agents_graph.invoke({"question": question})

        print("\nFinal Result:")
        print(result)

        validator = result["validator"]

        if validator.get("dashboard", False):
            print("\n📊 DASHBOARD MODE TRIGGERED")

            raw_dashboard = run_dashboard_agent(question)
            dashboard_questions = json.loads(clean_json(raw_dashboard))
            print(dashboard_questions)
            print(dashboard_questions['questions'])
            dashboard_questions = dashboard_questions['questions']
            print("\nGenerated Dashboard Questions:")
            for q in dashboard_questions:
                print(" -", q)

            # Run each dashboard question through full pipeline
            paths = []
            for dq in dashboard_questions:

                print("\n➡ Dashboard Question:", dq)

                sub_result = agents_graph.invoke({"question": dq})

                sql = sub_result["sql_query"]
                sql_result = run_sql(dq, sql)

                if not sql_result["success"]:
                    print("Skipping failed dashboard SQL…")
                    continue

                append_result_to_csv(dq, sql, sql_result["data"], dashboard_mode=True)

                if sub_result["validator"].get("visualization", True):

                    visual_spec = run_visualization_agent(
                        sub_result["validator"]["analysis_goal"],
                        sql_result["data"].head(2),
                        sql_result["data"].columns.tolist()
                    )

                    visual_json = clean_json(visual_spec)

                    path, fig = render_plotly(sql_result["data"], visual_json)

                    print("Saved dashboard chart:", path)
                    paths.append(path)
                    build_dashboard(paths)


            print("\n✅ Dashboard complete")

            print("--------------------------------------------------")
            continue

        sql = result["sql_query"]
        print("\nExecuting SQL query...")
        sql_result = run_sql(question, sql)

        # Feedback loop on failure
        if not sql_result["success"]:
            print("Running feedback loop...")

            fixed_sql = run_sql_feedback_agent(
                question=sql_result["question"],
                sql=sql_result["sql"],
                error=sql_result["error"] or sql_result["reason"]
            )

            sql_result = run_sql(question, fixed_sql)

            if not sql_result["success"]:
                print("\n SQL failed twice — skipping visualization.")
                append_result_to_csv(question, sql, None)
                print("--------------------------------------------------")
                continue

        # Save results
        append_result_to_csv(question, sql, sql_result["data"])

        visual_flag = validator.get("visualization", False)

        if visual_flag and sql_result["success"]:
            visual_agent = run_visualization_agent(
                validator["analysis_goal"],
                sql_result["data"].head(2),
                sql_result["data"].columns.tolist()
            )

            visual_json = clean_json(visual_agent)

            path, fig = render_plotly(sql_result["data"], visual_json)

            print("Rendered plot:", path)
        else:
            print("Visualization skipped.")

        print("--------------------------------------------------")
