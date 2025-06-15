import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def download_image(image_url, local_filename):
    """
    Downloads an image from a given URL and saves it to a local file.

    Parameters:
    - image_url: The URL of the image to download.
    - local_filename: The path where the image will be saved locally.

    Returns:
    - The local_filename if download is successful, None otherwise.
    """
    try:
        print(f"Attempting to download image from: {image_url}")
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # Raise an exception for HTTP errors

        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image downloaded successfully to: {local_filename}")
        return local_filename
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        return None


def register_image(user_id):
    """
    Step 1: Register an image to be uploaded to LinkedIn
    
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
                "urn:li:digitalmediaRecipe:feedshare-image"
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
        print("Image registration successful!")
        result = response.json()
        
        # Extract the important values
        upload_url = result["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset = result["value"]["asset"]
        
        return {
            "upload_url": upload_url,
            "asset": asset
        }
    else:
        print(f"Error registering image: {response.status_code}")
        print(response.text)
        return None


def upload_image_binary(upload_url, image_path):
    """
    Step 2: Upload the image binary file to LinkedIn
    
    Parameters:
    - upload_url: The URL provided by the registration step
    - image_path: Path to the image file on your system
    
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
    
    # Check if the image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return False
    
    # Open the image file in binary mode
    with open(image_path, 'rb') as image_file:
        # Make the POST request with the binary file
        response = requests.post(upload_url, headers=headers, data=image_file)
    
    # Check for successful response
    if response.status_code in [200, 201]:
        print("Image binary upload successful!")
        return True
    else:
        print(f"Error uploading image binary: {response.status_code}")
        print(response.text)
        return False


def create_image_share(user_id, asset, share_text, title=None, description=None, visibility="PUBLIC"):
    """
    Step 3: Create the image share on LinkedIn
    
    Parameters:
    - user_id: Your LinkedIn user ID
    - asset: The asset URN from the registration step
    - share_text: The text commentary for your post
    - title: Optional title for the image
    - description: Optional description for the image
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
                "shareMediaCategory": "IMAGE",
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
        print(f"Image share created successfully! Status code: {response.status_code}")
        # Get the post ID from the X-RestLi-Id header
        post_id = response.headers.get('X-RestLi-Id')
        if post_id:
            print(f"Post ID: {post_id}")
        return response.json()
    else:
        print(f"Error creating image share: {response.status_code}")
        print(response.text)
        return None


def share_image_post(image_paths, share_text, titles=None, descriptions=None, visibility="PUBLIC"):
    """
    Complete process to share multiple images in a single LinkedIn post.

    Parameters:
    - image_paths: List of image file paths (local paths, not URLs)
    - share_text: The text commentary for your post
    - titles: Optional list of titles (same length as image_paths or None)
    - descriptions: Optional list of descriptions (same length as image_paths or None)
    - visibility: Post visibility (PUBLIC, CONNECTIONS, or LOGGED_IN)

    Returns:
    - Response from LinkedIn API or None if any step fails
    """
    # Get user ID from environment variables
    user_id = os.getenv('LINKEDIN_USER_ID')
    if not user_id:
        raise ValueError("LinkedIn User ID not found in environment variables")

    if not image_paths or not isinstance(image_paths, list):
        raise ValueError("image_paths must be a non-empty list")

    media_assets = []

    for idx, image_path in enumerate(image_paths):
        # Step 1: Register the image
        registration = register_image(user_id)
        if not registration:
            print(f"Failed to register image: {image_path}")
            return None

        # Step 2: Upload the image binary
        upload_success = upload_image_binary(registration["upload_url"], image_path)
        if not upload_success:
            print(f"Failed to upload image: {image_path}")
            return None

        # Step 3: Add to media asset list
        media_obj = {
            "status": "READY",
            "media": registration["asset"]
        }

        # Attach individual title/description if available
        if titles and idx < len(titles) and titles[idx]:
            media_obj["title"] = {"text": titles[idx]}
        if descriptions and idx < len(descriptions) and descriptions[idx]:
            media_obj["description"] = {"text": descriptions[idx]}

        media_assets.append(media_obj)

    # Step 4: Create the combined post with all media
    url = "https://api.linkedin.com/v2/ugcPosts"
    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    if not access_token:
        raise ValueError("LinkedIn OAuth token not found in environment variables")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": share_text
                },
                "shareMediaCategory": "IMAGE",
                "media": media_assets
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code in [200, 201]:
        print("Image share created successfully!")
        post_id = response.headers.get('X-RestLi-Id')
        if post_id:
            print(f"Post ID: {post_id}")
        return response.json()
    else:
        print(f"Error creating image share: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # URL of the image you want to upload
    image_url_from_error = "https://res.cloudinary.com/dxqqdr2te/image/upload/v1749980204/public_images/jdhzfi3vunvvqx58wuyz.png"
    local_image_path = "downloaded_image.png" # The local file name where the image will be saved

    # Download the image first
    downloaded_file = download_image(image_url_from_error, local_image_path)

    if downloaded_file:
        # Now you can use the local file path to share the image
        share_text = "Here‘s How to Stop It Before It’s Too Late."
        image_title = ""
        image_description = ""
        
        # Share the image post
        result = share_image_post(
            image_paths=[downloaded_file], # Pass the local file path here
            share_text=share_text,
            titles=[image_title],
            descriptions=[image_description]
        )
        
        if result:
            print("Response data:")
            print(json.dumps(result, indent=2))
        
        # Clean up the downloaded file (optional)
        try:
            if os.path.exists(local_image_path):
                os.remove(local_image_path)
                print(f"Cleaned up local file: {local_image_path}")
        except Exception as e:
            print(f"Error cleaning up file: {e}")
    else:
        print("Image download failed, cannot proceed with LinkedIn post.")
