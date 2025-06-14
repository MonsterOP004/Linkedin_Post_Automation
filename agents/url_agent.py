from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import BraveSearch  # Example for web searching/scraping
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv

load_dotenv()

# You might need a dedicated web scraping tool or a more advanced summarization agent

class URLAnalyzerAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant")
        # Using BraveSearch as an example tool that can potentially return page content
        # For more robust scraping, consider tools like `requests` + `BeautifulSoup` or `Playwright`
        self.search_tool = BraveSearch(name="brave_search", description="Use this to search the internet and get content from URLs. Input should be a search query or a URL.")

        self.agent_executor = initialize_agent(
            tools=[self.search_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
        )

    def run(self, url: str) -> dict:
        print(f"URL Analyzer Agent: Attempting to analyze URL: {url}")
        # The agent will try to use the search_tool to get information from the URL
        query = f"Access and summarize the main content of the following URL for a LinkedIn post, extract key points, and identify the tone of the source: {url}"
        try:
            response = self.agent_executor.run(query)

            # This part is crucial: parsing the agent's free-form response into structured JSON.
            # A common approach is to pass the agent's response to another LLM call with a specific JSON schema.
            # For simplicity here, we'll try to extract patterns, but this is less robust.
            # A more robust solution would involve defining a specific output format for the URL analysis agent,
            # and then parsing it with Pydantic.

            # Example of trying to parse. This is heuristic and might need refinement.
            summary = ""
            main_points = []
            tone = "Unknown"

            # Use another prompt to structure the output if the agent doesn't directly return JSON
            structuring_prompt = ChatPromptTemplate.from_template("""
            Given the following analysis from a web Browse agent, extract the summary, main points (as a list), and the tone of the source.

            Agent Output:
            {agent_output}

            Return your analysis in this JSON format:
            {{
              "summary": "<summary>",
              "main_points": ["<point1>", "<point2>"],
              "tone_of_source": "<tone>"
            }}
            """)
            structuring_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
            structured_response = (structuring_prompt | structuring_llm).invoke({"agent_output": response})

            parsed = {}
            try:
                parsed = eval(structured_response.content) # Using eval for quick parse of string JSON, use json.loads for production
                return parsed
            except Exception as e:
                print(f"Error parsing structured response from URL analysis: {e}. Raw response: {structured_response.content}")
                # Fallback to direct agent response if parsing fails
                summary = response
                main_points = []
                tone = "Uncertain"
                return {
                    "summary": summary,
                    "main_points": main_points,
                    "tone_of_source": tone
                }

        except Exception as e:
            print(f"URL Analyzer Agent failed to run: {e}")
            return {
                "summary": f"Could not analyze URL: {url}. Error: {e}",
                "main_points": [],
                "tone_of_source": "Failed"
            }


url_analyser_agent = URLAnalyzerAgent()