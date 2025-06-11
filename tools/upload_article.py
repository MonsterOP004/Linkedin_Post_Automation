import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def share_article(share_text, article_url, title=None, description=None, visibility="PUBLIC"):
    """
    Share an article on LinkedIn
    
    Parameters:
    - share_text: The text commentary for your post
    - article_url: The URL of the article to share
    - title: Optional title for the article
    - description: Optional description for the article
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)
    
    Returns:
    - Response from LinkedIn API
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    
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
    
    # Prepare the media object exactly as shown in the documentation
    media = {
        "status": "READY",
        "originalUrl": article_url
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
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Check for successful response
    if response.status_code in [200, 201]:
        print(f"Article shared successfully! Status code: {response.status_code}")
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
    # Example article post with the exact text from your example
    commentary = "Learning more about LinkedIn by reading the LinkedIn Blog!"
    article_url = "https://blog.linkedin.com/"
    article_title = "Official LinkedIn Blog"
    article_description = "Official LinkedIn Blog - Your source for insights and information about LinkedIn."
    
    # Share the article
    result = share_article(
        share_text=commentary,
        article_url=article_url,
        title=article_title,
        description=article_description
    )
    
    if result:
        print("Response data:")
        print(json.dumps(result, indent=2))

