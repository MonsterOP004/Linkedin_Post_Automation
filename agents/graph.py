# graph.py
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import Optional, Literal
from langchain_core.runnables import RunnableLambda
from .models import CriticOutput, WriterOutput, ResearchOutput, ImageAnalysisOutput, URLAnalysisOutput, VideoAnalysisOutput
from .critic_agent import critic_agent
from .writer_agent import writer_agent
from .researcher_agent import research_agent
from .url_agent import url_agent
from .image_agent import image_analyser_agent
from .video_agent import video_analyser_agent
import json # Import json module

MAX_REWRITES = 3

class AgentState(BaseModel):
    topic: str
    description: str
    tone: str
    audience: str
    intent: str
    word_limit: int
    type: Literal["text", "url", "image", "video"]
    url: Optional[str] = None
    research_summary: Optional[str] = None
    url_analysis: Optional[URLAnalysisOutput] = None
    image_analysis: Optional[ImageAnalysisOutput] = None
    video_analysis: Optional[VideoAnalysisOutput] = None
    post: Optional[str] = None
    score: Optional[float] = None
    critique: Optional[str] = None
    iteration_count: int = 0

def should_rewrite(state: AgentState) -> str:
    """
    Determines if the post needs to be rewritten based on score and iteration count.
    """
    if (state.score is None or state.score < 7) and state.iteration_count < MAX_REWRITES:
        print(f"Critique score ({state.score}) is below 7 or not set. Rewriting. Iteration: {state.iteration_count}/{MAX_REWRITES}")
        return "writer"
    else:
        if state.score is not None and state.score >= 7:
            print(f"Critique score ({state.score}) is 7 or higher. Ending graph.")
        else:
            print(f"Max rewrites ({MAX_REWRITES}) reached. Ending graph despite score ({state.score}).")
        return END

def url_analysis_wrapper(state: AgentState) -> AgentState:
    """
    Invokes the URL analysis agent and updates the state.
    """
    if state.url:
        print(f"Starting URL analysis for: {state.url}")
        analysis_output = url_agent.invoke(state.url)
        # Assuming url_agent returns a direct Pydantic model or dict
        state.url_analysis = analysis_output
        state.research_summary = analysis_output.summary
        print(f"URL analysis complete. Summary: {state.url_analysis.summary[:100]}...")
    else:
        print("No URL provided for URL analysis, skipping.")
    return state

def image_analysis_wrapper(state: AgentState) -> AgentState:
    """
    Invokes the image analysis agent and updates the state.
    """
    if state.url:
        print(f"Starting Image analysis for: {state.url}")
        response = image_analyser_agent.invoke({"image_url": state.url})
        try:
            # Clean the output string before parsing
            cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
            parsed = ImageAnalysisOutput.parse_raw(cleaned_content)
            state.image_analysis = parsed
            state.research_summary = parsed.description
            print(f"Image analysis complete. Description: {state.image_analysis.description[:100]}...")
        except Exception as e:
            print(f"Error parsing image analysis output: {e}")
            state.image_analysis = ImageAnalysisOutput(description=f"Failed to analyze image from {state.url}.", key_elements=[], sentiment="Unknown")
            state.research_summary = state.image_analysis.description
    else:
        print("No URL provided for image analysis, skipping.")
    return state

def video_analysis_wrapper(state: AgentState) -> AgentState:
    """
    Invokes the video analysis agent and updates the state.
    """
    if state.url:
        print(f"Starting Video analysis for: {state.url}")
        response = video_analyser_agent.invoke({"video_url": state.url})
        try:
            # Clean the output string before parsing
            cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
            parsed = VideoAnalysisOutput.parse_raw(cleaned_content)
            state.video_analysis = parsed
            state.research_summary = parsed.summary
            print(f"Video analysis complete. Summary: {state.video_analysis.summary[:100]}...")
        except Exception as e:
            print(f"Error parsing video analysis output: {e}")
            state.video_analysis = VideoAnalysisOutput(summary=f"Failed to analyze video from {state.url}.", key_moments=[], sentiment="Unknown")
            state.research_summary = state.video_analysis.summary
    else:
        print("No URL provided for video analysis, skipping.")
    return state


def research_wrapper(state: AgentState) -> AgentState:
    """
    Performs general web research if no specific content analysis is present.
    """
    if state.research_summary and (state.type == "url" or state.type == "image" or state.type == "video"):
        print("Skipping general research as specific content analysis (URL/Image/Video) is available.")
        return state

    print("Starting general research.")
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
    result = research_agent.invoke({"input": query})
    try:
        # Assuming research_agent might return a dict or a string depending on its setup
        if isinstance(result, dict) and "summary" in result:
             state.research_summary = result["summary"]
        elif isinstance(result, str):
            # Clean the output string if it's a string from the agent (e.g., with markdown)
            cleaned_result = result.strip().replace("```json", "").replace("```", "").strip()
            parsed = ResearchOutput.parse_raw(cleaned_result)
            state.research_summary = parsed.summary
        else:
            state.research_summary = str(result)
    except Exception as e:
        print(f"Error parsing research output: {e}")
        state.research_summary = f"Could not generate a good research summary. Raw: {result}"
    return state


def writer_wrapper(state: AgentState) -> AgentState:
    """
    Invokes the writer agent, incorporating URL, image, or video analysis if available.
    """
    print("Starting writer agent.")
    
    writer_input_data = state.dict()
    
    if state.type == "url" and state.url_analysis:
        writer_input_data["research_summary"] = (
            f"Key insights from the linked article: {state.url_analysis.summary}. "
            f"Main points include: {', '.join(state.url_analysis.main_points)}. "
            f"The original source's tone is {state.url_analysis.tone_of_source}."
        )
        writer_input_data["description"] = f"{state.description}. Based on the content from {state.url}."
    elif state.type == "image" and state.image_analysis:
        writer_input_data["research_summary"] = (
            f"Image analysis: {state.image_analysis.description}. "
            f"Key elements: {', '.join(state.image_analysis.key_elements)}. "
            f"Overall sentiment: {state.image_analysis.sentiment}."
        )
        writer_input_data["description"] = f"{state.description}. Based on the image at {state.url}."
    elif state.type == "video" and state.video_analysis:
        writer_input_data["research_summary"] = (
            f"Video analysis summary: {state.video_analysis.summary}. "
            f"Key moments: {', '.join(state.video_analysis.key_moments)}. "
            f"Overall sentiment: {state.video_analysis.sentiment}."
        )
        writer_input_data["description"] = f"{state.description}. Based on the video at {state.url}."
    elif not state.research_summary:
         writer_input_data["research_summary"] = "No external research or content analysis available."

    response = writer_agent.invoke(writer_input_data)
    try:
        # Clean the output string before parsing
        cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        parsed = WriterOutput.parse_raw(cleaned_content)
        state.post = parsed.content
    except Exception as e:
        print(f"Error parsing writer output: {e}")
        state.post = response.content # Keep raw content in case of parsing failure for debugging
    return state


def critic_wrapper(state: AgentState) -> AgentState:
    """
    Invokes the critic agent and updates the state with score and critique.
    """
    print("Starting critic agent.")
    response = critic_agent.invoke({
        "post": state.post,
        "intent": state.intent,
        "tone": state.tone,
        "audience": state.audience
    })
    try:
        # Clean the output string before parsing
        cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        parsed = CriticOutput.parse_raw(cleaned_content)
        avg_score = (parsed.clarity + parsed.tone + parsed.engagement + parsed.relevance) / 4
        state.score = avg_score
        state.critique = parsed.suggestion
    except Exception as e:
        print(f"Error parsing critic output: {e}")
        state.score = 5 # Assign a default score if parsing fails
        state.critique = "Failed to parse critic output. Please refine model response."
    
    state.iteration_count += 1
    print(f"Critic Score: {state.score}, Iteration: {state.iteration_count}")
    print(f"Critique: {state.critique}")
    return state


graph = StateGraph(AgentState)

# Add all nodes
graph.add_node("url_analyzer", RunnableLambda(url_analysis_wrapper))
graph.add_node("image_analyzer", RunnableLambda(image_analysis_wrapper))
graph.add_node("video_analyzer", RunnableLambda(video_analysis_wrapper))
graph.add_node("research", RunnableLambda(research_wrapper))
graph.add_node("writer", RunnableLambda(writer_wrapper))
graph.add_node("critic", RunnableLambda(critic_wrapper))

# Set entry point with conditional routing based on 'type'
graph.set_entry_point("research")

graph.add_conditional_edges(
    "research",
    lambda state: {
        "url": "url_analyzer",
        "image": "image_analyzer",
        "video": "video_analyzer",
        "text": "writer"
    }.get(state.type, "writer"),
    {
        "url_analyzer": "url_analyzer",
        "image_analyzer": "image_analyzer",
        "video_analyzer": "video_analyzer",
        "writer": "writer"
    }
)

# After analysis, go to writer
graph.add_edge("url_analyzer", "writer")
graph.add_edge("image_analyzer", "writer")
graph.add_edge("video_analyzer", "writer")

# Continue the flow
graph.add_edge("writer", "critic")

# Critic decides whether to loop back or end
graph.add_conditional_edges(
    "critic",
    should_rewrite,
    {
        "writer": "writer",
        END: END
    }
)

app = graph.compile()

# For visualization (optional)
print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()