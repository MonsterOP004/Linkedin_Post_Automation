from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import Optional,Literal
from langchain_core.runnables import RunnableLambda
from .models import CriticOutput, WriterOutput, ResearchOutput, ImageAnalysisOutput, URLAnalysisOutput, VideoAnalysisOutput
from .critic_agent import critic_agent
from .writer_agent import writer_agent
from .researcher_agent import research_agent

MAX_REWRITES = 3

class AgentState(BaseModel):
    topic: str
    description: str
    tone: str
    audience: str
    intent: str
    word_limit: int
    research_summary: Optional[str] = None
    post: Optional[str] = None
    score: Optional[float] = None
    critique: Optional[str] = None
    iteration_count: int = 0

def should_rewrite(state: AgentState) -> str:

    if (state.score is None or state.score < 7) and state.iteration_count < MAX_REWRITES:
        print(f"Critique score ({state.score}) is below 7 or not set. Rewriting. Iteration: {state.iteration_count}/{MAX_REWRITES}")
        return "writer"
    else:
        if state.score is not None and state.score >= 7:
            print(f"Critique score ({state.score}) is 7 or higher. Ending graph.")
        else:
            print(f"Max rewrites ({MAX_REWRITES}) reached. Ending graph despite score ({state.score}).")
        return END

def research_wrapper(state: AgentState) -> AgentState:
    query = f"""
        {state.topic} — {state.description}

        Using web search tools, gather recent insights and examples related to the topic.
        Then summarize the findings in 2–3 sentences suitable for a LinkedIn post.
        Avoid links, focus on facts, stats, or tool names if possible.
        Use a {state.tone} tone.

        Respond in this JSON format:
        {{
          "summary": "<summary>"
        }}
    """
    result = research_agent.run(query)
    try:
        parsed = ResearchOutput.parse_raw(result)
        state.research_summary = parsed.summary
    except Exception:
        state.research_summary = result
    return state


def writer_wrapper(state: AgentState) -> AgentState:
    response = writer_agent.invoke(state.dict())
    try:
        parsed = WriterOutput.parse_raw(response.content)
        state.post = parsed.content
    except Exception:
        state.post = response.content
    return state


def critic_wrapper(state: AgentState) -> AgentState:
    response = critic_agent.invoke({
        "post": state.post,
        "intent": state.intent,
        "tone": state.tone,
        "audience": state.audience
    })
    try:
        parsed = CriticOutput.parse_raw(response.content)
        avg_score = (parsed.clarity + parsed.tone + parsed.engagement + parsed.relevance) / 4
        state.score = avg_score
        state.critique = parsed.suggestion
    except Exception:
        state.score = 5
        state.critique = "Failed to parse critic output. Please refine model response."
    
    state.iteration_count += 1 
    print(f"Critic Score: {state.score}, Iteration: {state.iteration_count}")
    print(f"Critique: {state.critique}")
    return state



graph = StateGraph(AgentState)

graph.add_node("research", RunnableLambda(research_wrapper))
graph.add_node("writer", RunnableLambda(writer_wrapper))
graph.add_node("critic", RunnableLambda(critic_wrapper))

graph.set_entry_point("research")
graph.add_edge("research", "writer")
graph.add_edge("writer", "critic")

graph.add_conditional_edges(
    "critic",
    should_rewrite,
    {
        "writer": "writer",
        END: END
    }
)

app = graph.compile()

print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

#pip install grandalf