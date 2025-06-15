# url_agent.py
import requests
import json
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from .models import URLAnalysisOutput 

load_dotenv()

RENDER_API_BASE_URL = os.getenv("RENDER_API_BASE_URL", "https://linkedin-url-summary-extractor.onrender.com")

def call_render_url_summarizer_api(url: str) -> dict:
    """
    Calls your deployed Render API's /url_content_summarizer endpoint.
    Returns the full JSON response from the API.
    """
    endpoint = "/url_content_summarizer"
    full_api_url = f"{RENDER_API_BASE_URL}{endpoint}"

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "url": url
    }

    try:
        response = requests.post(full_api_url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Render URL summarizer API for {url}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "url": url,
            "analysis": {
                "main_topic": "Error",
                "key_points": [],
                "summary": f"Failed to retrieve content from {url}."
            }
        }

def url_analysis_runnable(url: str) -> URLAnalysisOutput:
    """
    This function will be wrapped by RunnableLambda.
    It takes a URL, calls the Render API, and maps the response
    to the URLAnalysisOutput Pydantic model.
    """
    api_response = call_render_url_summarizer_api(url)
    
    if api_response.get("status") == "success":
        analysis_data = api_response.get("analysis", {})
        try:
            return URLAnalysisOutput(
                summary=analysis_data.get("summary", "No summary provided."),
                main_points=analysis_data.get("key_points", []),
                tone_of_source="Informative"
            )
        except Exception as e:
            print(f"Error parsing URL analysis output from API response for {url}: {e}")
            return URLAnalysisOutput(
                summary=f"Failed to parse detailed analysis from {url}. Error: {e}",
                main_points=["Parsing error encountered."],
                tone_of_source="Unknown"
            )
    else:
        error_message = api_response.get("message", "Unknown API error during URL summarization.")
        analysis_data = api_response.get("analysis", {}) 
        return URLAnalysisOutput(
            summary=analysis_data.get('summary', error_message),
            main_points=analysis_data.get('key_points', []),
            tone_of_source="Error"
        )

url_agent = RunnableLambda(url_analysis_runnable)