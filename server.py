from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from agents.graph import app as langgraph_app, AgentState
from tools.upload_content import ContentUploader
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploader = ContentUploader()

class ContentRequest(BaseModel):
    topic: str
    description: str
    tone: str
    audience: str
    intent: str
    word_limit: int = 250
    type: str
    url: str = None
    
class TextResponse(BaseModel):
    
    post_content : str
    post_visibility : str

# for both URL and Article
class URLResponse(BaseModel):
    
    post_title : str
    post_content : str
    post_url : str
    post_visibility : str

class ImageResponse(BaseModel):
    
    post_content : str
    post_image : List[str]
    post_visibility : str

class VideoResponse(BaseModel):
    
    post_title : str
    post_content : str
    post_video : str
    post_visibility : str

@app.get("/")
async def root():
    return {"message": "Welcome To Linkedin Server!!!"}
    
@app.post("/generate_linkedin_content")
async def generate_linkedin_content(request_data: ContentRequest):

    state = AgentState(
        topic=request_data.topic,
        tone=request_data.tone,
        description=request_data.description,
        audience=request_data.audience,
        intent=request_data.intent,
        word_limit=request_data.word_limit,
        type=request_data.type,
        url=request_data.url,
        research_summary=None,
        url_analysis=None,
        image_analysis=None,
        video_analysis=None,
        post=None,
        score=None,
        critique=None,
        iteration_count=0
    )

    result = langgraph_app.invoke(state)

    return result

@app.post("/post_linkedin_text_content")
async def post_linkedin_text_content(request_data: TextResponse):
    try:

        
        if not request_data.post_content or not request_data.post_visibility:
            raise HTTPException(status_code=400, detail="Missing required fields")

        response = uploader.upload_text_content(
            request_data.post_content,
            request_data.post_visibility
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/post_linkedin_url_content")
async def post_linkedin_url_content(request_data: URLResponse):
    try:


        if not request_data.post_title or not request_data.post_content or not request_data.post_url or not request_data.post_visibility:
            raise HTTPException(status_code=400, detail="Missing required fields")

        response = uploader.upload_url_content(
            request_data.post_content,
            request_data.post_url,
            request_data.post_title,
            request_data.post_visibility        
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post_linkedin_image_content")
async def post_linkedin_image_content(request_data: ImageResponse):
    try:


        if not request_data.post_content or not request_data.post_image or not request_data.post_visibility:
            raise HTTPException(status_code=400, detail="Missing required fields")

        response = uploader.upload_image_content(
            request_data.post_content,
            request_data.post_image,
            request_data.post_visibility
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post_linkedin_video_content")
async def post_linkedin_video_content(request_data: VideoResponse):
    try:


        if not request_data.post_title or not request_data.post_content or not request_data.post_video or not request_data.post_visibility:
            raise HTTPException(status_code=400, detail="Missing required fields")

        response = uploader.upload_video_content(
            request_data.post_title,
            request_data.post_content,
            request_data.post_video,
            request_data.post_visibility
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8889, reload=True)