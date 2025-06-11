import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def share_text_post(text_content, visibility="PUBLIC"):
    """
    Share a text post on LinkedIn
    
    Parameters:
    - text_content: The text content of your post
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)
    
    Returns:
    - Response from LinkedIn API
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    

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
    
    # Prepare the post payload exactly as shown in the documentation
    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "NONE"
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
        print(f"Post shared successfully! Status code: {response.status_code}")
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
    # Example post text
    post_text = "Hello World! This is my first Share on LinkedIn!"
    
    # Share the post
    result = share_text_post(post_text)
    
    if result:
        print("Response data:")
        print(json.dumps(result, indent=2))

