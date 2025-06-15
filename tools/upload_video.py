import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def register_video(user_id):
    """
    Step 1: Register a video to be uploaded to LinkedIn
    
    Parameters:
    - user_id: Your LinkedIn user ID
    
    Returns:
    - Dictionary containing uploadUrl and asset information
    """
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    
    # Get authentication token from environment variables
    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    if not access_token:
        raise ValueError("LinkedIn OAuth token not found in environment variables")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the registration payload
    payload = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-video"
            ],
            "owner": f"urn:li:person:{user_id}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Check for successful response
    if response.status_code == 200:
        print("Video registration successful!")
        result = response.json()
        
        # Extract the important values
        upload_url = result["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset = result["value"]["asset"]
        
        return {
            "upload_url": upload_url,
            "asset": asset
        }
    else:
        print(f"Error registering video: {response.status_code}")
        print(response.text)
        return None


def upload_video_binary(upload_url, video_path):
    """
    Step 2: Upload the video binary file to LinkedIn
    
    Parameters:
    - upload_url: The URL provided by the registration step
    - video_path: Path to the video file on your system
    
    Returns:
    - Boolean indicating success or failure
    """
    # Get authentication token from environment variables
    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    if not access_token:
        raise ValueError("LinkedIn OAuth token not found in environment variables")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False
    
    # Open the video file in binary mode
    with open(video_path, 'rb') as video_file:
        # Make the POST request with the binary file
        response = requests.post(upload_url, headers=headers, data=video_file)
    
    # Check for successful response
    if response.status_code in [200, 201]:
        print("Video binary upload successful!")
        return True
    else:
        print(f"Error uploading video binary: {response.status_code}")
        print(response.text)
        return False


def create_video_share(user_id, asset, share_text, title=None, description=None, visibility="PUBLIC"):
    """
    Step 3: Create the video share on LinkedIn
    
    Parameters:
    - user_id: Your LinkedIn user ID
    - asset: The asset URN from the registration step
    - share_text: The text commentary for your post
    - title: Optional title for the video
    - description: Optional description for the video
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)
    
    Returns:
    - Response from LinkedIn API
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    # Get authentication token from environment variables
    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    if not access_token:
        raise ValueError("LinkedIn OAuth token not found in environment variables")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Prepare the media object
    media = {
        "status": "READY",
        "media": asset
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
    
    # Prepare the post payload
    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": share_text
                },
                "shareMediaCategory": "VIDEO",
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
        print(f"Video share created successfully! Status code: {response.status_code}")
        # Get the post ID from the X-RestLi-Id header
        post_id = response.headers.get('X-RestLi-Id')
        if post_id:
            print(f"Post ID: {post_id}")
        return response.json()
    else:
        print(f"Error creating video share: {response.status_code}")
        print(response.text)
        return None


def share_video_post(video_path, share_text, title=None, description=None, visibility="PUBLIC"):
    """
    Complete process to share a video post on LinkedIn
    
    Parameters:
    - video_path: Path to the video file on your system
    - share_text: The text commentary for your post
    - title: Optional title for the video
    - description: Optional description for the video
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)
    
    Returns:
    - Response from LinkedIn API or None if any step fails
    """
    # Get user ID from environment variables
    user_id = os.getenv('LINKEDIN_USER_ID')
    if not user_id:
        raise ValueError("LinkedIn User ID not found in environment variables")
    
    # Step 1: Register the video
    registration = register_video(user_id)
    if not registration:
        return None
    
    # Step 2: Upload the video binary
    upload_success = upload_video_binary(registration["upload_url"], video_path)
    if not upload_success:
        return None
    
    # Step 3: Create the video share
    result = create_video_share(
        user_id=user_id,
        asset=registration["asset"],
        share_text=share_text,
        title=title,
        description=description,
        visibility=visibility
    )
    
    return result


# Example usage
if __name__ == "__main__":
    # Example video post
    video_path = "finalvid.mp4"  
    share_text = "Urban Snap Video"
    video_title = "Urban Snap Video 1"
    video_description = ""
    
    # Share the video post
    result = share_video_post(
        video_path=video_path,
        share_text=share_text,
        title=video_title,
        description=video_description
    )
    
    if result:
        print("Response data:")
        print(json.dumps(result, indent=2))

