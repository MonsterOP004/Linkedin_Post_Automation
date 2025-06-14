from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

video_analysis_prompt = ChatPromptTemplate.from_template("""
You are an AI assistant specialized in analyzing video content for LinkedIn posts.
Analyze the following video data (e.g., a transcript, summary, or description) and extract:
1. A brief summary of the video's content.
2. Key moments or topics discussed in the video.
3. The overall sentiment or tone of the video.

Video data/transcript/summary: {video_url}

Return your analysis in **this JSON format**:
{{
  "summary": "<summary>",
  "key_moments": ["<moment1>", "<moment2>"],
  "sentiment": "<sentiment>"
}}
""")

llm_video_analyser = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

video_analyser_agent = video_analysis_prompt | llm_video_analyser