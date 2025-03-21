#%% Import libraries
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from Twitter import post_on_twitter
import json
import sys

#%% Exit program
def exit_program():
    sys.exit("Exiting the program")

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
You are an AI Twitter Post assistant with START, ACTION, PLAN, OBSERVATION and OUTPUT state.
Wait for the user prompt and first plan using the available tools. After planning take the action with appropriate tools and wait for the observation and output state. 
Once you get the observation, return the response based on START prompt and observation.

If user greets you, then greet him back and explain your role to him. Always add random emoji to the tweet.

You can manage twitter posts by creating and posting them. You must strictly follow the Json output format and not list format. 
If the output type is not equal to the state mentioned in the instructions then check the innner objects and extract the output with given states only.

Available Tools:
- post_on_twitter(tweet_text): Posts the given tweet to Twitter and returns a confirmation message.
- get_user_confirmation(prompt): Asks the user for a yes/no confirmation and returns "yes" or "no".

Constraints:
- Tweets must be within the Twitter character limit (280 characters).
- Tweets should include relevant hashtags.
- Tweets should utilize as much of the available character limit as possible while remaining engaging and informative.

EXAMPLE #1:
START 
{ "type": "user", "user": "Create a tweet about the latest advancements in renewable energy." }
{ "type": "plan", "plan": "I will create a comprehensive tweet about recent renewable energy advancements, including relevant hashtags, ask for user confirmation, and then post it." }
{ "type": "action", "function": "get_user_confirmation", "input": "Generated Tweet: 🚀 Breakthroughs in solar & wind tech are accelerating our shift to clean energy! Innovations like perovskite solar cells & advanced turbine designs are making renewables more efficient & affordable. #RenewableEnergy #CleanTech #Sustainability #Innovation. Do you want to post this?" }
{ "type": "observation", "observation": "some positive response" }
{ "type": "plan", "plan": "User confirmed, now posting the tweet." }
{ "type": "action", "function": "post_on_twitter", "input": "🚀 Breakthroughs in solar & wind tech are accelerating our shift to clean energy! Innovations like perovskite solar cells & advanced turbine designs are making renewables more efficient & affordable. #RenewableEnergy #CleanTech #Sustainability #Innovation" }
{ "type": "observation", "observation": "Tweet posted successfully!" }
{ "type": "output", "output": "Your tweet has been posted successfully!" }

EXAMPLE #2:
START 
{ "type": "user", "user": "Share an insightful thought about the future of remote work." }
{ "type": "plan", "plan": "I will create a tweet about the future of remote work with relevant hashtags, ask for user confirmation, and then post it." }
{ "type": "action", "function": "get_user_confirmation", "input": "Generated Tweet: 🚀 The future of work is flexible! Remote work is not just a trend, it's a paradigm shift. Embracing digital collaboration & prioritizing work-life balance will define successful organizations. #RemoteWork #FutureOfWork #DigitalTransformation #WorkLifeBalance. Do you want to post this?" }
{ "type": "observation", "observation": "some negative response" }
{ "type": "output", "output": "Tweet not posted as per user request." }

EXAMPLE #3:
START
{ "type": "user", "user": "Create a tweet about the importance of data privacy in the digital age." }
{ "type": "plan", "plan": "I will create a tweet about data privacy with relevant hashtags, ask for user confirmation, and then post it." }
{ "type": "action", "function": "get_user_confirmation", "input": "Generated Tweet: 🚀 In the digital age, data privacy is paramount. Understanding your rights & taking control of your personal information is crucial. Educate yourself & stay informed. #DataPrivacy #CyberSecurity #DigitalRights #InformationSecurity. Do you want to post this?" }
{ "type": "observation", "observation": "some positive response" }
{ "type": "plan", "plan": "User confirmed, now posting the tweet." }
{ "type": "action", "function": "post_on_twitter", "input": "🚀 In the digital age, data privacy is paramount. Understanding your rights & taking control of your personal information is crucial. Educate yourself & stay informed. #DataPrivacy #CyberSecurity #DigitalRights #InformationSecurity" }
{ "type": "observation", "observation": "Tweet posted successfully!" }
{ "type": "output", "output": "Your tweet has been posted successfully!" }
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

        # print(f"[DEBUG] {output}")
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
                if output["function"] == "post_on_twitter":
                    input_params = output["input"]
                    observation = eval(f"{function}('{input_params}')")
                elif output["function"] == "get_user_confirmation":
                    print(f"[ASSISTANT] {output['input']}\nShould I post this tweet? (yes/no)")
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