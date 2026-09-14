#------utils----
from math import sqrt

def calculate(operation, a, b=None):

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        return a / b

    elif operation == "power":
        return a ** b

    elif operation == "sqrt":
        return sqrt(a)

    else:
        raise ValueError(f"Unknown operation: {operation}")

def greet(name):
    return (f"Hello {name}, Good day!")

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "A tool to calculate mathematical expression",
            "parameters":{
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string", 
                        "description": "A mathematical unary or binary operation in english small letters (e.g: add, divide)"
                    },
                    "a":{
                        "type": "number",
                        "description": "First operand for the operation" 
                    },
                    "b": {
                        "type": "number",
                        "description": "Optional second operand for the operation. Only provide when operation is binary"
                    }
                }
            },
            "required": ["operation", "a"],
        }
    },
    {
        "type": "function",
        "function": {
            "name": "greet",
            "description": "A tool to greet someone",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of person or any entity to greet"
                    }
                }
            },
            "required": ["name"]
        }
    }
]

tool_registry = {
    "calculator": {
        "function": calculate,
        "schema": {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "A tool to calculate mathematical expression",
                "parameters":{
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string", 
                            "enum": [
                                "add",
                                "subtract",
                                "multiply",
                                "divide",
                                "power",
                                "sqrt"
                            ],
                            "description": "Mathematical operation to perform."
                        },
                        "a":{
                            "type": "number",
                            "description": "First operand for the operation" 
                        },
                        "b": {
                            "type": "number",
                            "description": "Optional second operand for the operation. Only provide when operation is binary"
                        }
                    }
                },
                "required": ["operation", "a"],
            }
        }
    },

    "greet": {
        "function": greet,
        "schema": {
            "type": "function",
            "function": {
                "name": "greet",
                "description": "A tool to greet someone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of person or any entity to greet"
                        }
                    }
                },
                "required": ["name"]
            }
        }
    }
}

tools = [tool["schema"] for tool in tool_registry.values()]
#---------------

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OR_API_KEY")
)

session = [{"role": "user", "content": "Greet Mr. Ali, and tell him what is square of 124 * 33"}]

while True:

    #1. LLM interpert the task and decide the tool/action
    response = client.chat.completions.create(
        model='qwen/qwen3-8b',
        messages=session,
        tools=tools
    )
    message = response.choices[0].message
    session.append(message)

    if message.tool_calls:

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name
            parameters = json.loads(tool_call.function.arguments)

            print(f"LLM requested tool: {tool_name}")
            print(f"Parameters: {parameters}")

            tool = tool_registry.get(tool_name)

            if not tool:
                tool_result = f"Unknow tool: {tool_name}"
            else:
                tool_result = tool["function"](**parameters)
            

            print(f"Tool Result: {tool_result}")

            session.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tool_call.id
            })

    else:

        print(f"Final Answer: {message.content}")

        break