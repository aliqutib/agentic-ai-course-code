#------utils----
from math import sqrt

def calculate(operation, a, b=None):

    if not isinstance(a, (int, float)):
        raise TypeError("Parameter 'a' must be a number")

    if b is not None and not isinstance(b, (int, float)):
        raise TypeError("Parameter 'b' must be a number")
    
    if (b is not None):
        if operation == "add":
            return a + b

        elif operation == "subtract":
            return a - b

        elif operation == "multiply":
            return a * b

        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b

        elif operation == "power":
            return a ** b
        else:
            raise ValueError(f"Unknown binary operation: {operation}")
    else:
        if operation == "sqrt":
            return sqrt(a)
        else:
            raise ValueError(f"Unknown Unary operation: {operation} OR if you mean Binary operation, it need two operands")



def greet(name):
    return (f"Hello {name}, Good day!")

tool_definitions = [
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

tool_implementations = {"calculator": calculate, "greet": greet}

tools = tool_definitions
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

session = [{"role": "user", "content": "Find mod of 12"}]

MAX_ITERATION = 5
MAX_RETIRES  = 2
retires  = 0
for _ in range(MAX_ITERATION):
    
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

            tool = tool_implementations.get(tool_name)

            if not tool:
                tool_result = f"Unknow tool: {tool_name}"
            else:
                try:
                    tool_result = tool(**parameters)
                    success = True 
                except Exception as e:
                    tool_result = f"Tool execution failed: {e}"
                    success = False
                    retires += 1
                    if retires  >= MAX_RETIRES:
                        print("Agent stopped: maximum retries reached.")
                        break
            

            print(f"Tool Result: {tool_result}")

            session.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tool_call.id
            })

    else:
        print(f"Final Answer: {message.content}")
        break
else:
    print("Agent Stopped")