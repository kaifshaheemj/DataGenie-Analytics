import pandas as pd

def append_result_to_csv(question: str, sql: str, df: pd.DataFrame, path="data_3.csv", dashboard_mode=False):
    if df is not None:
        data_preview = df.head(5).to_json()
    else:
        data_preview = None or "SQL_FAILED"

    
    record = {
        "question": question,
        "sql_query": sql,
        "data_preview": data_preview 
    }

    result_df = pd.DataFrame([record])

    try:
        existing = pd.read_csv(path)
        combined = pd.concat([existing, result_df], ignore_index=True)
        combined.to_csv(path, index=False)
    except FileNotFoundError:
        result_df.to_csv(path, index=False)
    print(f"Results saved to {path}")
