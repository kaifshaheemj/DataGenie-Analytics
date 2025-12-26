
def load_schema_text():
    path = "C:\\DataGenie\\schema\\CSV_ATTRIBUTES_WITH_KEYS.md"
    with open(path, "r", encoding="utf-8") as f:
        print("Loading schema from:", path)
        content = f.read()
        print("Schema loaded successfully.")
        return content