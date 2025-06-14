import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def share_url_post(share_text, url, title=None, description=None, visibility="PUBLIC"):
    """
    Share a URL post on LinkedIn
    
    Parameters:
    - share_text: The text commentary for your post
    - url: The URL to share
    - title: Optional title for the URL preview
    - description: Optional description for the URL preview
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)
    
    Returns:
    - Response from LinkedIn API
    """
    url_endpoint = "https://api.linkedin.com/v2/ugcPosts"
    
    # Get authentication token from environment variables
    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    if not access_token:
        raise ValueError("LinkedIn OAuth token not found in environment variables")
    
    # Get user ID from environment variables or use the get_user_id.py script
    user_id = os.getenv('LINKEDIN_USER_ID')
    if not user_id:
        raise ValueError("LinkedIn User ID not found in environment variables")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Prepare the media object
    media = {
        "status": "READY",
        "originalUrl": url
    }
    
    # Add optional title if provided
    if title:
        media["title"] = {
            "text": title
        }
    
    # Add optional description if provided
    if description:
        media["description"] = {
            "text": description
        }
    
    # Prepare the post payload exactly as shown in the documentation
    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": share_text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [media]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility
        }
    }
    
    # Make the POST request
    response = requests.post(url_endpoint, headers=headers, data=json.dumps(payload))
    
    # Check for successful response
    if response.status_code in [200, 201]:
        print(f"URL post shared successfully! Status code: {response.status_code}")
        # Get the post ID from the X-RestLi-Id header
        post_id = response.headers.get('X-RestLi-Id')
        if post_id:
            print(f"Post ID: {post_id}")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__ == "__main__":

    commentary = "ChatGPT Is Poisoning Your Brain…"
    article_url = "https://medium.com/@jordan_gibbs/chatgpt-is-poisoning-your-brain-b66c16ddb7ae"
    article_title = "ChatGPT Is Poisoning Your Brain HAHAHA…"
    article_description = ""
    
    result = share_url_post(
        share_text=commentary,
        url=article_url,
        title=article_title,
        description=article_description
    )
    
    if result:
        print("Response data:")
        print(json.dumps(result, indent=2))

