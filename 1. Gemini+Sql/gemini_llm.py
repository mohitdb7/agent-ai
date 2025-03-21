#%% Import libraries
from mysqlConnection import add_new_todo, get_all_todos, get_todo, delete_todo
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import sys

def exit_program():
    sys.exit("Exiting the program")


#%% Declare prompt
SYS_Prompt = """
You are an AI Todo List assistant with START, ACTION, PLAN, OBSERVATION and OUTPUT state.
Wait for the user prompt and first plan using the available tools. After planning take the action with appropriate tools and wait for the observation and output state. 
Once you get the observation, return the response based on START promot and observation.

You can manage tasks by adding, deleting, updating and Viewing. You must strictly follow the Json output format and not list format. 
If the output type is not equal to the state mentioned in the instructions then check the innner objects and extract the output with given states only.

Todo DB Schema:
id: String and Primary Key
task: String

Available Tools:
- get_all_todos(): Returns all the todos in the database
- add_new_todo(task): Adds a new todo to the database with the given task as string and returns the id and task in the Json format
- delete_todo(task): Deletes a todo from the database with the given task as string
- get_todo(task): Returns a todo from the database with the given task as string
- exit_program(): Exits the program

EXAMPLE #1:
START 
{ "type": "user", "user": "I want to shop for some milk, fruits, vegetables" }
{ "type": "plan", "plan": "I will use the add_new_todo to create a new Todo in DB" }
{ "type": "action", "function": "add_new_todo", "input": "Shop for milk, fruits, vegetables" }
{ "type": "observation", "observation": "{"id" : "2", "task" : "Shop for milk, fruits, vegetables"}" }
{ "type": "output", "output": "Your Todo item is added successfully" }

Example #2:
START 
{ "type": "user", "user": "Delete all the tasks" }
{ "type": "plan", "plan": "I will first get all the tasks from from the database using the get_all_todos" }
{ "type": "action", "function": "get_all_todos", "input": "" }
{ "type": "observation", "observation": "[{"id" : "2", "task" : "Shop for milk, fruits, vegetables"}]" }
{ "type": "plan", "plan": "I will use the task list from the get_all_todos result and call delete_todo for each task" }
{ "type": "action", "function": "delete_todo", "input": "Shop for milk, fruits, vegetables" }
{ "type": "observation", "observation": "{"result" : "True", "task" : "Shop for milk, fruits, vegetables"}" }
{ "type": "output", "output": "Your Todo item is deleted successfully" }

EXAMPLE #3:
START 
{ "type": "user", "user": "Get all Tasks" }
{ "type": "plan", "plan": "I will use the get_all_todos to get all the tasks from the database" }
{ "type": "action", "function": "get_all_todos", "input": "" }
{ "type": "observation", "observation": "[{"id" : "1", "task" : "Practice AI Agent"}, {"id" : "2", "task" : "Shop for milk, fruits, vegetables"}]" }
{ "type": "output", "output": "Your Your Tasks for today are \n - Practice AI Agent \n - Shop for milk, fruits, vegetables" }


Example #4:
START 
{ "type": "user", "user": "Exit" }
{ "type": "plan", "plan": "I will exit the program" }
{ "type": "action", "function": "exit_program", "input": "" }
{ "type": "output", "output": "Exiting the program" }
"""
#%% Define Keys
GOOGLE_API_KEY = open("../Keys/gemini_API_Key.txt", "r").read().strip()
genai.configure(api_key=GOOGLE_API_KEY)

#%% Declare Model
MODEL = 'gemini-2.0-flash' #'gemini-1.5-flash'
model = genai.GenerativeModel(MODEL)

message = [{
        "role": "model",
        "parts": SYS_Prompt
    }]

#%% Run Logic
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
    
    # temp_messsage = message
    # temp_messsage.append(user_message)

    while True:
        chat_completion_json = model.generate_content(str(message), 
                                            generation_config=gen_config)
        output = json.loads(chat_completion_json.candidates[0].content.parts[0].text)

        # print(f"[DEBUG] {output}")
        message.append({"role" : "model", "parts" : output})
        try:
            if output["type"] == "output":                
                message = [{
                        "role": "model",
                        "parts": SYS_Prompt
                    }]
                                
                print(f"[ASSISTANT] {output['output']}")
                break
            elif output["type"] == "action":
                function = output["function"]
                input_params = None
                if output["function"] == "add_new_todo":
                    input_params = output["input"]
                    observation = eval(f"{function}('{input_params}')")
                elif output["function"] == "get_all_todos":
                    observation = eval(f"{function}()")
                elif output["function"] == "delete_todo":
                    input_params = output["input"]
                    observation = eval(f"{function}('{input_params}')")
                elif output["function"] == "exit_program":
                    observation = eval(f"{function}()")

                
                # print(f"[DEBUG] {function} will be called with params {input_params}, {observation}")
                
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



# globals()[add_new_todo]()