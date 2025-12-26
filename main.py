from graph.story_graph import story_graph

if __name__ == "__main__":
    print("Hello from main.py")

    question = "Show me revenue by product category"

    result = story_graph.invoke({"question": question})

    print(result["story_plan"])
