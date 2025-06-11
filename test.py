import requests

URL = "http://127.0.0.1:8889/generate_linkedin_content"

payload = {
    "topic": "The impact of AI on modern hiring processes",
    "description": "AI tools like resume parsers and chatbots are now core to talent acquisition workflows.",
    "tone": "Professional and slightly conversational",
    "audience": "Tech recruiters, HR professionals, and startup founders",
    "intent": "Inform and engage",
    "word_limit": 250
}

def test_generate_content():
    response = requests.post(URL, json=payload)
    
    print("✅ Status Code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print("\n📄 Generated Post:\n", data["post"])
        print("\n🧠 Critique:")
        print("Score:", data["score"])
        print("Suggestion:", data["critique"])
    else:
        print("❌ Failed:", response.text)

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
