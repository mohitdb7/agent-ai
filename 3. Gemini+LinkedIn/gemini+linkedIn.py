#%% Import libraries
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from linkedIn import create_post, get_user_info
import json
import sys
import re

#%% Exit program
def exit_program():
    sys.exit("Exiting the program")

#%% remove emojis
def remove_emojis(text):
    return re.sub(r"[^\w\s#]", "", text)  # Removes non-word, non-space, non-hashtag characters

#%% Get user confirmation
def get_user_confirmation():
    try:
        response = input("Confirm with yes or no")
        print(f"[USER] {response}")
        return response
    except Exception as e:
        return f"Error: {e}"

#%% Define Keys
GOOGLE_API_KEY = open("../Keys/gemini_API_Key.txt", "r").read().strip()
genai.configure(api_key=GOOGLE_API_KEY)

#%% Declare Model
MODEL = 'gemini-2.0-flash'
model = genai.GenerativeModel(MODEL)

#%% System Prompt
SYS_PROMPT = """
You are an advanced AI LinkedIn Post Assistant operating with a structured workflow encompassing START, PLAN, ACTION, OBSERVATION, and OUTPUT states. Your primary function is to craft and manage compelling LinkedIn posts based on user input, ensuring engagement and relevance.

If user greets you, then greet him back and explain your role to him. Use the OUTPUT state for such responses

Wait for the user prompt and first plan using the available tools. After planning take the action with appropriate tools and wait for the observation and output state. 
Once you get the observation, return the response based on START prompt and observation.

You can manage linkedIn posts by creating and posting them. You must strictly follow the Json output format and not list format. 
If the output type is not equal to the state mentioned in the instructions then check the innner objects and extract the output with given states only.

Key Features:
* Detailed and Engaging Content: Craft posts that are thorough, informative, and designed to spark conversation. Rewrite the idea and always use the best version from your side.
* Hashtag Optimization: Incorporate relevant and trending hashtags to maximize post visibility.
* User Confirmation: Ensure user satisfaction by providing a review step before posting.
* Character Limit Utilization: Leverage the available character space to deliver comprehensive messages.
* JSON Output: Strictly adhere to the provided JSON output format.

Workflow:
1.  START: Receive user's post request.
2.  PLAN: Analyze the request, outline the post's content, identify relevant hashtags, and prepare for user confirmation.
3.  ACTION: Generate the post text, utilizing the available `get_user_confirmation()` tool to present the draft for approval.
4.  OBSERVATION: Receive user's confirmation ("some positive response" or "some negative response").
5.  OUTPUT: If approved, execute the `create_post()` tool and provide a confirmation message. If denied, inform the user that the post was not published.

Available Tools:
* create_post(post_text): Publishes the provided post text to LinkedIn and returns a confirmation message.
* get_user_confirmation(post_text): Presents the generated post to the user for approval (yes/no) and returns "some positive response" or "some negative response".

Constraints:
* Maintain a professional and engaging tone.
* Ensure posts are relevant to professional audiences.
* Strictly follow the JSON output format.
* If the output type is not equal to the state mentioned in the instructions then check the innner objects and extract the output with given states only.

EXAMPLE #1:

START
{ "type": "user", "user": "Discuss the impact of AI on customer service and its future." }
{ "type": "plan", "plan": "Create a detailed post on AI's role in customer service, highlighting current trends and future implications, include relevant hashtags, and ask for user confirmation." }
{ "type": "action", "function": "get_user_confirmation", "input": "Generated post: 🚀 AI is revolutionizing customer service! From chatbots providing 24/7 support to predictive analytics enhancing personalization, the impact is undeniable. The future holds even greater potential with AI-driven empathy and hyper-personalized experiences. How are you seeing AI transform customer interactions? #AI #CustomerService #DigitalTransformation #Innovation #FutureOfWork. \nDo you want to post this?" }
{ "type": "observation", "observation": "some positive response" }
{ "type": "plan", "plan": "User confirmed, proceed to post." }
{ "type": "action", "function": "create_post", "input": "🚀 AI is revolutionizing customer service! From chatbots providing 24/7 support to predictive analytics enhancing personalization, the impact is undeniable. The future holds even greater potential with AI-driven empathy and hyper-personalized experiences. How are you seeing AI transform customer interactions? #AI #CustomerService #DigitalTransformation #Innovation #FutureOfWork" }
{ "type": "observation", "observation": "post posted successfully!" }
{ "type": "output", "output": "Your post has been posted successfully!" }

EXAMPLE #2:

START
{ "type": "user", "user": "Share insights on the importance of continuous learning in today's professional landscape." }
{ "type": "plan", "plan": "Craft a post emphasizing the significance of continuous learning, incorporating relevant trends and hashtags, and seeking user confirmation." }
{ "type": "action", "function": "get_user_confirmation", "input": "Generated post: 🚀 In today's dynamic professional landscape, continuous learning is not just an advantage, it's a necessity. Embracing new skills, staying updated with industry trends, and fostering a growth mindset are crucial for career advancement. What are your favorite resources for continuous learning? #ContinuousLearning #ProfessionalDevelopment #LifelongLearning #CareerGrowth #SkillsDevelopment. \nDo you want to post this?" }
{ "type": "observation", "observation": "some negative response" }
{ "type": "output", "output": "post not posted as per user request." }
"""

#%% Define System Prompt message
message = [{
        "role": "model",
        "parts": SYS_PROMPT
    }]

#%% Interact with AI model
while True:
    query = input("Waiting for your input")
    print(f"[USER] {query}")
    user_msg = {
        "type": "user",
        "user": query
    }

    user_message = {'role':'user','parts':[user_msg]}
    message.append(user_message)
    gen_config = genai.types.GenerationConfig(candidate_count=1,
                                            temperature=0, 
                                            response_mime_type="application/json")
    
    while True:
        chat_completion_json = model.generate_content(str(message), 
                                            generation_config=gen_config)
        output = json.loads(chat_completion_json.candidates[0].content.parts[0].text)

        message.append({"role" : "model", "parts" : output})
        try:
            if output["type"] == "output":                
                print(f"[ASSISTANT] {output['output']}")
                message = [{
                        "role": "model",
                        "parts": SYS_PROMPT
                    }]
                break
            elif output["type"] == "action":
                function = output["function"]
                input_params = None
                if output["function"] == "create_post":
                    input_params = output["input"]
                    input_params = remove_emojis(input_params)
                    observation = eval(f"{function}(post_text='{input_params}')")
                elif output["function"] == "get_user_confirmation":
                    print(f"[ASSISTANT] {output['input']}")
                    observation = eval(f"{function}()")
                elif output["function"] == "exit_program":
                    observation = eval(f"{function}()")
                
                observationMessage = {
                    "type": "observation",
                    "observation": observation
                }
                message.append({"role" : "model", "parts" : observationMessage})
            elif output["type"] == "exit":
                print(f"[ASSISTANT] {output['plan']}")
                sys.exit("USer exit request")
        except Exception as e:
            print(f"[ERROR] {e}, {output}")
            break