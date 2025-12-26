import os
from dotenv import load_dotenv

load_dotenv()
path = os.getenv("SCHEMA_PATH")

def load_schema_text():
   
    with open(path, "r", encoding="utf-8") as f:
        print("Loading schema from:", path)
        content = f.read()
        print("Schema loaded successfully.")
        return content