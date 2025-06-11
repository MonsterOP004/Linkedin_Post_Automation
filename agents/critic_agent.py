from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate

critic_prompt = ChatPromptTemplate.from_template("""
You're a critical LinkedIn content reviewer.

Evaluate the following post on a scale of 1–10 for:
1. Clarity
2. Tone alignment
3. Engagement
4. Relevance to the given intent

Post:
{post}

User Intent: {intent}  
Tone: {tone}  
Audience: {audience}

Then provide a 2-line improvement suggestion.

Return your feedback in **this JSON format**:
{{
  "clarity": <score>,
  "tone": <score>,
  "engagement": <score>,
  "relevance": <score>,
  "suggestion": "<tip>"
}}
""")

llm = ChatMistralAI(model="devstral-small-2505")

critic_agent = critic_prompt | llm
