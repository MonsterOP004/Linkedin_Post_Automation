from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

image_analysis_prompt = ChatPromptTemplate.from_template("""
You are an AI assistant specialized in analyzing images for LinkedIn content.
Analyze the following image data or description and provide:
1. A concise description of the image.
2. Key elements or objects present in the image.
3. The overall sentiment or mood conveyed by the image (e.g., professional, innovative, collaborative, formal, informal).

Image data/path/description: {image_url}

Return your analysis in **this JSON format**:
{{
  "description": "<description>",
  "key_elements": ["<element1>", "<element2>"],
  "sentiment": "<sentiment>"
}}
""")

llm_image_analyser = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2) # Example: assuming Gemini Pro Vision

image_analyser_agent = image_analysis_prompt | llm_image_analyser