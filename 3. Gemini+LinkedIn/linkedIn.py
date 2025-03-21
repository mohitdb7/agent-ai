#%% Run code
import requests
import json

with open('../Keys/linkedIn.txt') as json_file:
            LINKEDIN_KEY = json.load(json_file)
        
ACCESS_TOKEN = LINKEDIN_KEY["auth_token"]
URN = LINKEDIN_KEY["urn"]

def get_user_info(ACCESS_TOKEN):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Your LinkedIn User details are", data)
        print("Your LinkedIn User URN:", data["sub"])
    else:
        print("Error:", response.status_code, response.text)


def create_post(post_text):
    userId = URN
    print("*"*50, "Preparing your post", "*"*50)
    # print("Post is", post_text)
    # print("Access token is", ACCESS_TOKEN)
    # print("User ID is", userId)

    # Your LinkedIn user ID (URN format)
    USER_URN = f"urn:li:person:{userId}"

    # API URL
    URL = "https://api.linkedin.com/v2/ugcPosts"

    # Post content
    data = {
        "author": USER_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Encode the payload properly
    # json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")


    # Headers
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    # Make the request
    response = requests.post(URL, json=data, headers=headers)

    # Check response
    if response.status_code == 201:
        print("Post successfully created!")
    else:
        print(f"Error: {response.status_code}, {response.text}")