from langchain_groq import ChatGroq
from langchain_community.tools import TavilySearchResults
from langchain.agents import initialize_agent, tool
import datetime
from dotenv import load_dotenv

load_dotenv()

@tool
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current system date and time in the specified format.
    Default format: YYYY-MM-DD HH:MM:SS
    """
    return datetime.datetime.now().strftime(format)


tavily_search_results = TavilySearchResults(
    search_depth="basic",
    name="tavily_search_results", 
    description="Use this to search for current information on the internet. Input should be a search query string."
)


tools = [tavily_search_results, get_current_time]


llm = ChatGroq(
    model="llama-3.1-8b-instant",
)


research_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=2,
    return_direct=True,  
)
