# NexusRaven
NexusRaven is a package for dropping NexusRavenV2 into any OpenAI-compatible Function Calling application!

## What is NexusRaven-V2?

NexusRaven-V2 is a function calling model that is capable of generating single, nested, and parallel function calls, allowing it to serve as a powerful open source alternative to OpenAI's function calling API. 

NexusRaven-V2 surpasses GPT4 in function calling benchmarks, and is more versatile than the OpenAI Function Calling API, which is constrained to only generating single or parallel calls. 

For more information about NexusRaven-V2, please refer to the [Github Page](https://github.com/nexusflowai/NexusRaven)🚡🚡 and the [HuggingFace Model Page](https://huggingface.co/Nexusflow/NexusRaven-V2-13B/)!

## What Purpose Does This Package Serve?

NexusRaven is a package to interact with NexusRaven-V2 Function Calling using OpenAI semantics. This allows NexusRaven-V2 to be a drop-in replacement to any existing project that uses OpenAI function calling with very minor changes necessary!

## How Do I Use This Package?

NexusRaven can be used just like you would use any OpenAI Function Calling application!

OR, if you'd prefer, you can directly provide your Python functions to NexusRaven-V2 and let it use those functions!

## Are There Examples?

YES! 

- [OpenAI-like function calling](https://github.com/nexusflowai/nexusraven-pip/tree/master/examples/openai_fc)
- [Python function calling](https://github.com/nexusflowai/nexusraven-pip/tree/master/examples/python_fc)


## Using NexusRaven-V2 Function Calling via Package

### Please first setup your own NexusRaven-V2 endpoint to use!

[Please follow this guide to set up your TGI endpoint and retrieve the URL and the Key!](https://huggingface.co/docs/inference-endpoints/guides/create_endpoint). Please ensure you use [the NexusRaven-V2](https://huggingface.co/Nexusflow/NexusRaven-V2-13B) model when setting up the endpoint.

We STRONGLY recommend the following:
1. Please EXPLICITLY disable quantization (bits-and-bytes) when creating your endpoint. Uncaliberated quantization affects accuracy a lot, and we recommend setting this to None. It will be under "Advanced Configuration"
2. Please set your max input lengths to 8K. While it is fine to keep it lower, RavenV2 will benefit from a longer max length. If you use a lower setting, please make sure you pass max\_new\_tokens in your create() call appropriately.

Once you have this done, please refer to the rest of this document for using NexusRaven-V2's function calls!

### Providing Functions For NexusRaven-V2 To Use

```python
import nexusraven

# Example Derived from: https://cobusgreyling.medium.com/practical-examples-of-openai-function-calling-a6419dc38775
client = nexusraven.Client(api_url = <YOUR_TGI_URL>, api_key=<YOUR_TGI_KEY>)
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
    include_reasoning = True,
    tool_choice="auto",  # auto is default, but we'll be explicit
)
```

You can also set the 'include_reasoning = True' flag to make NexusRaven-V2 generate explanations for you! Please set it to False to save on tokens.

Please set 'max\_new\_tokens' to the limit of your TGI endpoint.

The example above will return the following:

```python
{
    'choices': [
        {
            'message': {
                'tool_calls': [
                    {
                        'id': '',
                        'type': 'function',
                        'function': {
                            'name': 'order_detail',
                            'arguments': {
                                'to_address': "22 Fourth Avenue, Woodlands",
                                'order': "2 packs of cans",
                                'date': "27th of July",
                                'notes': "Just leave the order at the door, we live in a safe area."
                            }
                        }
                    }
                ],
                'reasoning': "Thought: The function call `order_detail(to_address='22 Fourth Avenue, Woodlands', order='2 packs of cans', date='27th of July', notes='Just leave the order at the door, we live in a safe area.')` answers the question because it provides the necessary information to capture the order.\n\nThe `to_address` parameter is set to '22 Fourth Avenue, Woodlands', which is the address where the order should be delivered.\n\nThe `order` parameter is set to '2 packs of cans', which is the detail of the order.\n\nThe `date` parameter is set to '27th of July', which is the date for delivery.\n\nThe `notes` parameter is set to 'Just leave the order at the door, we live in a safe area.', which are any delivery notes.\n\nTherefore, the function call provides all the necessary information to capture the order, which is to order two packs of cans and have it delivered to 22 Fourth Avenue, Woodlands on the 27th of July. The delivery notes are also included, which are to leave the order at the door and that the area is safe.",
                'raw_calls': ["order_detail(to_address='22 Fourth Avenue, Woodlands', order='2 packs of cans', date='27th of July', notes='Just leave the order at the door, we live in a safe area.')"]
            }
        }
    ]
}
```

Please notice how the \"raw\_calls\" contains the pythonic call, while the \"tool\_calls\" contain the OpenAI-like response JSON for easier parsing.

### Parsing Outputs

Raven will produce a structured JSON and a Raw Python Call for you. The return data structure will look like this: 

```python
 AttrDict({
    "choices": [AttrDict({
        "message": AttrDict({
            "tool_calls": tools, 
            "reasoning": reasoning, 
            "raw_calls": raw_calls
        })
    })]
})
```

If you would like to have your function calls in the [same way as OpenAI's Function Calling API returns it](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models), please utilize the "tool_calls" item.

If you would like to have your function calls as pure python function calls, please use the "raw_calls" item.

Optionally, if you would like NexusRaven-V2 to reason about its function use, and you have specified include_reasoning in your create call, you can use "reasoning" to pull NexusRaven-V2's reasoning.


### NO WARRANTY DISCLAIMER

#### Disclaimer of Warranty

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#### Usage Agreement

By using this software, you acknowledge that you have read this disclaimer, understand its contents, and agree to its terms. The use of the software is entirely at your own risk. The authors and contributors of this software shall not be held liable for any damage or loss resulting from its use.


