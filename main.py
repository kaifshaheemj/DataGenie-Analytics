from graph.agent_graph import agents_graph
from save_results import append_result_to_csv
from tools.data_extractor_tool import run_sql
from agents.sql_feedback_agent import run_sql_feedback_agent


if __name__ == "__main__":
    print("Hello from main.py")
    questions = [
        "What are our best-selling products?",
        "What is the total sales for last quarter?",
        "Which customer segments are most profitable over the last 12 months?",
        "Which products have the highest profit margin?",
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
        sql = result["sql_query"]
        print("Executing SQL query...", sql)
        result= run_sql(question, sql)
        if not result["success"]:
            print("Running feedback loop...")

            fixed_sql = run_sql_feedback_agent(
                question=result["question"],
                sql=result["sql"],
                error=result["error"] or result["reason"]
            )

            # run again
            second = run_sql(question, fixed_sql)

        print("Query Result DataFrame:")

        append_result_to_csv(question, sql, result["data"])

        print("--------------------------------------------------")
        break
    

    