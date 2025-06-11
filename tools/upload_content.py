from .upload_text import share_text_post
from .upload_url import share_url_post
from .upload_article import share_article
from .upload_image import share_image_post
from .upload_video import register_video, upload_video_binary
import os

class ContentUploader:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
        self.user_id = os.getenv('LINKEDIN_USER_ID')

    def upload_text_content(self,text_content,visibility):
        return share_text_post(text_content,visibility)

    def upload_url_content(self,share_text, url, title, description, visibility):
        return share_url_post(share_text, url, title, description, visibility)
    
    
    def upload_image_content(self,image_paths,share_text,title,description,visibility):
        return share_image_post(
            image_paths,
            share_text,
            titles,
            descriptions,
            visibility
        )
    
    def upload_video_content(self,video_path,share_text,title,description,visibility):
        return share_image_post(
            video_path,
            share_text,
            titles,
            descriptions,
            visibility
        )
    