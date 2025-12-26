import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    top_p=0.2, 
    max_output_tokens=2048,
    model_kwargs={"response_mime_type": "application/json"},
)
print("LLM initialized with Google Gemini-2.5-Flash model.")