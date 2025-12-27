import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def run_sql(question: str, sql: str):
    try:
        df = pd.read_sql(sql, engine)

        if df.empty:
            print("DB WARNING: Query returned no results.")

            return {
                "success": False,
                "reason": "empty_result",
                "error": None,
                "rows": 0,
                "data": df,
                "sql": sql,
                "question": question
            }

        print("DB SUCCESS: Retrieved", len(df), "rows.")

        return {
            "success": True,
            "reason": None,
            "error": None,
            "rows": len(df),
            "data": df,
            "sql": sql,
            "question": question
        }

    except Exception as e:
        print("DB ERROR:", e)

        return {
            "success": False,
            "reason": "db_error",
            "error": str(e),
            "rows": 0,
            "data": pd.DataFrame(),
            "sql": sql,
            "question": question
        }

    

