import nexusraven as OpenAI

# Example Derived from: https://cobusgreyling.medium.com/practical-examples-of-openai-function-calling-a6419dc38775
client = OpenAI.Client(api_url = "INSERT YOUR URL", api_key = "INSERT YOUR KEY")
messages = [
    {
      "role": "user",
      "content": "I would like to order two packs of cans, and have it delivered to 22 Fourth Avenue, Woodlands. I need this on the 27th of July. Just leave the order at the door, we live in a safe area."
    }
]

tools = [
  {
    "type" : "function",
    "function" : {
                    "name": "order_detail",
                    "description": "template to capture an order.",
                    "parameters": {
                      "type": "object",
                      "properties": {
                        "to_address": {
                          "type": "string",
                          "description": "To address for the delivery"
                        },
                        "order": {
                          "type": "string",
                          "description": "The detail of the order"
                        },
                         "date": {
                          "type": "string",
                          "description": "the date for delivery."
                        },
                         "notes": {
                          "type": "string",
                          "description": "Any delivery notes."
                        }
                      }
                    }
                  }
  }
  ]

response = client.chat.completions.create(
    model="ravenv2",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto is default, but we'll be explicit
)

print (response)




