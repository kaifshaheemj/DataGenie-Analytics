from graph.agent_graph import agents_graph
from save_results import append_result_to_csv
from tools.data_extractor_tool import run_sql
from tools.plots_render_tool import render_plotly
from utils.clean_utils import clean_json
from agents.sql_feedback_agent import run_sql_feedback_agent
from agents.visualization_agent import run_visualization_agent

if __name__ == "__main__":
    print("Hello from main.py")
    questions = [
        "Which products have the highest profit margin?",
        "What are our best-selling products?",
        "What is the total sales for last quarter?",
        "Which customer segments are most profitable over the last 12 months?",
        "Which customer segments are most profitable?"]
        # "What is the average selling price by category?",
        # "Which regions generate the most sales?",
        # "Which territories are growing vs declining?",
        # "Which age groups drive the most revenue?",
        # "What is our revenue, profit, and growth last month?"]
    for question in questions:
        print("\n\nQuestion:", question)
        result = agents_graph.invoke({"question": question})
        # print(result["validator"])
        # print("\nGenerated SQL for the query:")
        # print(result["sql_query"])
        print("\nFinal Result:")
        print(result)
        sql = result["sql_query"]
        print("Executing SQL query...", sql)
        result_sql = run_sql(question, sql)
        if not result_sql["success"]:
            print("Running feedback loop...")

            fixed_sql = run_sql_feedback_agent(
                question=result_sql["question"],
                sql=result_sql["sql"],
                error=result_sql["error"] or result_sql["reason"]
            )

            # run again
            second = run_sql(question, fixed_sql)


        print("Query Result DataFrame:")

        append_result_to_csv(question, sql, result_sql["data"])
        print("pi",result.get("validator", {}))
        print(result['validator'])
        visual_flag = result["validator"].get("visualization", False)
        print("Visualization flag from validator:", visual_flag)
        print(result["validator"]['analysis_goal'])
        if visual_flag:
            print("Visualization required for this query.")
            visual_agent =  run_visualization_agent(result["validator"]["analysis_goal"], result_sql["data"].head(2), result_sql["data"].columns.tolist())
            print("Visualization Agent Output:", visual_agent)
            visual_agent = clean_json(visual_agent)
            print("Cleaned Visualization JSON:", visual_agent)
            path, fig = render_plotly(result_sql["data"], visual_agent)
            print("Rendered plotly figure at path:", path)
            fig.show()
        
        print("--------------------------------------------------")
        # break
    

    