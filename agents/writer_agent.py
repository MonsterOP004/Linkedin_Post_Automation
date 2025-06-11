from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

writer_prompt = ChatPromptTemplate.from_template("""
You are a professional LinkedIn ghostwriter.

Write a {word_limit}-word post for LinkedIn using the following details:

- Topic: {topic}
- Description: {description}
- Research Summary: {research_summary}
- Tone: {tone}
- Audience: {audience}
- Intent: {intent}

Structure:
1. Start with a **catchy hook** that grabs attention.
2. Follow with the main body, weaving in relevant insights or stats from the research.
3. Embed the user's tone, audience context, and intent naturally throughout.
4. End with a reflective or actionable takeaway.
5. Ask a question to drive engagement.

Formatting rules:
- Do **not** use markdown formatting (e.g., no asterisks `*`, bold, or italic).
- Do **not** use quotation marks unless you're quoting someone.
- Only use hashtags (e.g., `#leadership`, `#techculture`) at the **end** of the post if appropriate.
- Use clear line breaks to format the post naturally.

Return the output in **this JSON format**:
{{
  "content": "<LinkedIn post>"
}}
""")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

writer_agent = writer_prompt | llm
