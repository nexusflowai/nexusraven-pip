import requests
from types import FunctionType
from ast import Constant, Expr, FunctionDef, Module, parse, Str, JoinedStr
import typing
import inspect
import ast
import logging
import re
import json

import requests
import ast
import logging
import json

class AttrDict(dict):
    """
    A dictionary subclass that supports attribute-style access.
    """
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'AttrDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'AttrDict' object has no attribute '{key}'")

class FunctionCallVisitor(ast.NodeVisitor):
    def visit_Call(self, node):
        function_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        arguments = [self._parse_arg(arg) for arg in node.args]
        keyword_arguments = {kw.arg: self._parse_arg(kw.value) for kw in node.keywords}
        return {"name": function_name, "arguments": arguments, "keywords": keyword_arguments}

    def visit_List(self, node):
        return [self._parse_arg(el) for el in node.elts]

    def visit_Dict(self, node):
        keys = [self._parse_arg(k) for k in node.keys]
        values = [self._parse_arg(v) for v in node.values]
        return dict(zip(keys, values))

    def _parse_arg(self, arg):
        if isinstance(arg, (ast.Str, ast.Num)):
            return arg.s
        elif isinstance(arg, ast.List):
            return [self._parse_arg(el) for el in arg.elts]
        elif isinstance(arg, ast.Dict):
            return self.visit(arg)
        elif isinstance(arg, ast.Call):
            return self.visit(arg)
        else:
            return ast.unparse(arg)

class Client:
    def __init__(self, api_url : str, api_key: str = None):
        self.api_key = api_key
        self.api_url = api_url
        self.chat = self.Chat(self, api_url, api_key)

    class Chat:
        def __init__(self, client, api_url, api_key = None):
            self.client = client
            self.completions = self.Completions(self, api_url, api_key)

        class Completions:
            def __init__(self, chat, api_url, api_key = None):
                self.chat = chat
                self.logger = self._initialize_logger()
                self.NEXUS_URL = api_url
                self.NEXUS_KEY = api_key

            def _python_type(self, json_type):
                """
                Maps JSON types to Python types.

                :param json_type: The JSON type as a string.
                :return: The corresponding Python type as a string.
                """
                type_mapping = {
                    "string": "str",
                    "number": "float",  # Default to float for general number handling
                    "integer": "int",
                    "boolean": "bool",
                    "array": "list",
                    "object": "dict"
                }
                return type_mapping.get(json_type, "str")  # Default to str for unrecognized types

            def _format_default_value(self, json_type, default):
                """
                Formats default values based on JSON type.

                :param json_type: The JSON type of the parameter.
                :param default: The default value of the parameter.
                :return: The formatted default value as a string.
                """
                if json_type in ["string", "array", "object"]:
                    return f"\"{default}\"" if default is not None else "None"
                elif json_type in ["number", "integer"]:
                    return str(default) if default is not None else "None"
                elif json_type == "boolean":
                    return "True" if default else "False"
                else:
                    return "None"

            def _generate_function_signature(self, name, params):
                """
                Generates the Python function signature from the function name and parameters.

                :param name: The name of the function.
                :param params: The parameters of the function.
                :return: A string representing the function signature.
                """
                signature = f"def {name}("
                args = []

                for param_name in params.keys():
                    param = params[param_name]
                    param_type = self._python_type(param["type"])
                    default = self._format_default_value(param["type"], param.get("default"))
                    args.append(f"{param_name}: {param_type} = {default}")

                signature += ", ".join(args) + "):"
                return signature

            def _generate_function_docstring(self, description, params):
                """
                Generates the docstring for the function.

                :param description: The description of the function.
                :param params: The parameters of the function.
                :return: A string representing the docstring of the function.
                """
                docstring = f'"""\n{description}\n\nParameters:\n'
                for param_name in params.keys():
                    param = params[param_name]
                    param_desc = param.get("description", "")
                    param_type = self._python_type(param["type"])
                    docstring += f'    {param_name} ({param_type}): {param_desc}\n'

                docstring += '"""\n'
                return docstring

            def _generate_function(self, tool):
                if not isinstance(tool, dict):
                    return self._generate_strings_from_py(tool)

                json_input = tool["function"]
                function_name = json_input["name"]
                description = json_input["description"]
                parameters = json_input["parameters"]
                function_signature = self._generate_function_signature(function_name, parameters["properties"])
                function_docstring = self._generate_function_docstring(description, parameters["properties"])
                return f"{function_signature}\n{function_docstring}"

            def _initialize_logger(self):
                logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                return logging.getLogger('nexusraven')

            def _extract_function_call_details(self, call_string):
                tree = ast.parse(call_string)
                visitor = FunctionCallVisitor()
                result = visitor.visit(tree.body[0].value)
                return AttrDict(result)

            def _convert_to_openai_api_format(self, function_call):
                parsed_call = self._extract_function_call_details(function_call)
                parsed_call["arguments"] = parsed_call["keywords"]
                del parsed_call["keywords"]
                api_format = {
                    "id": "",  # Unique ID generation logic here
                    "type": "function",
                    "function": parsed_call
                }
                api_format["function"]["arguments"] = json.dumps(api_format["function"]["arguments"])
                return AttrDict(api_format)

            def _parse_tool_calls(self, response_message):
                tool_calls = []
                raw_calls = []
                for line in response_message.strip().split(';'):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("Call:"):
                        line = line.replace("Call:", "").strip()
                    try:
                        tool_calls.append(self._convert_to_openai_api_format(line))
                    except:
                        self.logger.error("Looks like something went wrong parsing Raven's output into OpenAI Format! But you can still get the raw function call in Python format via 'raw_calls'.")
                        tool_calls.append(None)

                    raw_calls.append(line)
                return tool_calls, raw_calls

            def create(self, messages, tools=None, include_reasoning=False, max_new_tokens=2048, model="ravenv2", tool_choice="auto"):
                if model != "ravenv2":
                    self.logger.error("Only ravenv2 model supported!")
                    return None

                if tool_choice != "auto":
                    self.logger.error("Only auto tool choice supported!")
                    return None

                assert len(messages) == 1, "Only single message is supported"
                stop = ["</s>"] if include_reasoning else ["<bot_end>"]
                headers = self._build_headers()

                formatted_tools = [self._generate_function(tool) for tool in tools]

                payload = self._build_payload(formatted_tools, messages[0]['content'], max_new_tokens, stop)
                
                response = requests.post(self.NEXUS_URL, headers=headers, json=payload)
                return self._process_response(response, include_reasoning)

            def _generate_strings_from_py(self, func):
                # Get the full source code of the function
                obj_source = inspect.getsource(func)

                # Parse the source code into an Abstract Syntax Tree.
                module = ast.parse(obj_source)

                # The function definition is the first node in the module body.
                function_def = typing.cast(FunctionDef, module.body[0])

                # Extract the function signature
                signature = inspect.signature(func)
                func_signature = f"def {function_def.name}{signature}:"

                # Initialize docstring
                docstring = ""

                # Check if the first statement of the function is a docstring
                if len(function_def.body) > 0 and isinstance(function_def.body[0], Expr):
                    first_stmt = function_def.body[0].value

                    # Check for simple string docstring
                    if isinstance(first_stmt, (Str, Constant)):
                        docstring_value = first_stmt.s if isinstance(first_stmt, Str) else first_stmt.value
                        docstring = f'    """{docstring_value}"""'
                    
                    # Check for joined string docstring
                    elif isinstance(first_stmt, JoinedStr):
                        docstring_parts = []
                        for part in first_stmt.values:
                            if isinstance(part, Str):  # Python < 3.8
                                docstring_parts.append(part.s)
                            elif isinstance(part, Constant):  # Python >= 3.8
                                docstring_parts.append(part.value)
                        docstring_value = ''.join(docstring_parts)
                        docstring = f'    """{docstring_value}"""'
                # Combine the signature and the docstring
                combined_string = f"{func_signature}\n{docstring}"
                return combined_string

            def _build_headers(self):
                items = {
                    "Content-Type": "application/json"
                }
                if self.NEXUS_KEY:
                    items["Authorization"] = f"Bearer {self.NEXUS_KEY}"
                return items

            def _build_payload(self, formatted_tools, user_query, max_new_tokens, stop):
                return {
                    "inputs": "Function:\n" + "\nFunction:\n".join(formatted_tools) + "\n\nUser Query: " + user_query + "<human_end>",
                    "parameters": {"max_new_tokens": max_new_tokens, "return_full_text": False, "stop": stop, "do_sample": False, "temperature": 0.01}
                }

            def _process_response(self, response, include_reasoning):
                if not response.ok or "error" in response.json():
                    self.logger.error(f"An error occurred: {response.json()}")
                    return None

                response_data = response.json()[0]
                if include_reasoning:
                    try:
                        calls, reasoning = response_data["generated_text"].split("<bot_end>")
                        calls = calls.strip()
                        reasoning = reasoning.strip()
                    except:
                        # This version of TGI does not retain special tokens.
                        calls, reasoning = response_data["generated_text"].split("Thought:")
                        calls = calls.strip()
                        reasoning = "Thought: " + reasoning.strip()
                else:
                    calls, reasoning = response_data["generated_text"], None
                    calls = calls.strip()

                tools, raw_calls = self._parse_tool_calls(calls)
                return AttrDict({
                    "choices": [AttrDict({
                        "message": AttrDict({
                            "tool_calls": tools, 
                            "reasoning": reasoning, 
                            "raw_calls": raw_calls
                        })
                    })]
                })


