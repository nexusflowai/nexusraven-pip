import nexusraven as OpenAI
import json

# Example adapted from: https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models
client = OpenAI.Client(api_url = "API ENDPOINT FOR TGI", api_key = "API KEY")

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """
    Get the current weather in a given location
    
    Args:
        - location: The city and state, e.g. San Francisco, CA. Needs to be a latlong.
        - unit (optional): The temperature unit. Choose between celcius and fahrenheit
    """

    print (location)
    return None

def getlatlong(location):
    """
    Returns the latlong for a location. Give the location as a string and supports ONE city only!

    Args:
        - location: the location 
    """
    return [1024, 2048]

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role" : "user", "content" : "Can you get me the current weather for Paris, get it for San Francisco, and get it for New York?"}]
    tools = [
        get_current_weather,
        getlatlong
    ]
    response = client.chat.completions.create(
        model="ravenv2",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        return tool_calls
print(run_conversation())
