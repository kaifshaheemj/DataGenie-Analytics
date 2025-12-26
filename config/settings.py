import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,
    top_p=0.2, 
    max_output_tokens=2048,
    response_format="json",
)
print("LLM initialized with Google Gemini-2.5-Flash model.")