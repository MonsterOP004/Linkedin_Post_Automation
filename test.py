import requests

URL = "http://127.0.0.1:8889/generate_linkedin_content"

payload = {
    "topic": "The impact of AI on modern hiring processes",
    "description": "AI tools like resume parsers and chatbots are now core to talent acquisition workflows.",
    "tone": "Professional and slightly conversational",
    "audience": "Tech recruiters, HR professionals, and startup founders",
    "intent": "Inform and engage",
    "word_limit": 250,
    "type": "text"  # Added the 'type' field
}

# Payload for 'url' content
payload_url = {
    "topic": "Recent trends in remote work",
    "description": "Exploring the shift towards flexible work models and their benefits.",
    "tone": "Informative and analytical",
    "audience": "Business leaders, HR professionals, and remote workers",
    "intent": "Educate and discuss",
    "word_limit": 300,
    "type": "url",
    "url": "https://medium.com/@echoinstitute/the-future-of-remote-work-trends-and-predictions-what-is-remote-work-all-about-710c00c5099b"
}

# Payload for 'image' content
payload_image = {
    "topic": "Sustainable urban development",
    "description": "Showcasing eco-friendly city planning initiatives.",
    "tone": "Inspirational and forward-looking",
    "audience": "Urban planners, environmentalists, and policymakers",
    "intent": "Inspire and advocate",
    "word_limit": 150,
    "type": "image",
    "url": "https://stock.adobe.com/search/images?k=sustainable+city" # Example image URL
}

# Payload for 'video' content
payload_video = {
    "topic": "The future of renewable energy",
    "description": "Highlighting advancements in solar and wind power technologies.",
    "tone": "Optimistic and factual",
    "audience": "Energy investors, engineers, and general public interested in sustainability",
    "intent": "Inform and excite",
    "word_limit": 200,
    "type": "video",
    "url": "https://youtu.be/UVf2Yw7uFoE?si=Su6HtCK98fiyma9C" # Example video URL
}

def test_generate_content():
    response = requests.post(URL, json=payload_video)
    
    print("✅ Status Code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print("\n📄 Generated Post:\n", data["post"])
        print("\n🧠 Critique:")
        print("Score:", data["score"])
        print("Suggestion:", data["critique"])
    else:
        print("❌ Failed:", response.text)

# The test_generate_and_post_workflow function is not modified as per your request
def test_generate_and_post_workflow():
    # Generate content
    gen_response = requests.post(URL, json=payload)
    assert gen_response.status_code == 200
    generated_content = gen_response.json()
    
    # Post generated content
    post_payload = {
        "post_content": generated_content['post'],
        "post_visibility": "PUBLIC"
    }
    post_response = requests.post(
        "http://127.0.0.1:8889/post_linkedin_text_content",
        json=post_payload
    )
    
    post_result = post_response.json()
    print(post_result)


if __name__ == "__main__":
    test_generate_content()