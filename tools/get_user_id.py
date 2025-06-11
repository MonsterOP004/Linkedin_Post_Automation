import requests
import os
from dotenv import load_dotenv


load_dotenv(override=True)

def get_linkedin_user_info():

    access_token = os.getenv('LINKEDIN_OAUTH_TOKEN')
    
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__ == "__main__":
    
    user_info = get_linkedin_user_info()
    if user_info:
        print("User Info:")
        print(user_info)