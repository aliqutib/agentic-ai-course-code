#----Exceptions----

class ToolError(Exception):
    pass

class InvalidToolInput(ToolError):
    pass

class UnsupportedOperation(ToolError):
    pass

class NonRecoverableError(ToolError):
    pass

#------utils----
from math import sqrt

def calculate(operation, a, b=None):

    if not isinstance(a, (int, float)):
        raise InvalidToolInput("Parameter 'a' must be a number")

    if b is not None and not isinstance(b, (int, float)):
        raise InvalidToolInput("Parameter 'b' must be a number")
    
    if (b is not None):
        if operation == "add":
            return a + b

        elif operation == "subtract":
            return a - b

        elif operation == "multiply":
            return a * b

        elif operation == "divide":
            if b == 0:
                raise NonRecoverableError("Cannot divide by zero")
            return a / b

        elif operation == "power":
            return a ** b
        else:
            raise UnsupportedOperation(f"Unknown binary operation: {operation}")
    else:
        if operation == "sqrt":
            return sqrt(a)
        else:
            raise UnsupportedOperation(f"Unknown Unary operation: {operation} OR if you mean Binary operation, it need two operands")



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
                        "enum":["add", "subtract", "multiply", "divide", "power", "sqrt"], 
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

session = [{"role": "user", "content": "Greet Mr. Ali and find cube of 3"}]

MAX_ITERATION = 5
MAX_RETRIES  = 2
retries  = 0
should_stop = False
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

        print("tool call: ", message.tool_calls)
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

                except UnsupportedOperation as e:
                    retries += 1
                    tool_result = f"RECOVERABLE ERROR: {e}"
                    if retries  >= MAX_RETRIES:
                        print("Agent stopped: maximum retries reached.")
                        should_stop = True
    
                except InvalidToolInput as e:
                    retries += 1
                    tool_result = f"RECOVERABLE ERROR: {e}"
                    if retries  >= MAX_RETRIES:
                        print("Agent stopped: maximum retries reached.")
                        should_stop = True
    
                except NonRecoverableError as e:
                    tool_result = f"NON-RECOVERABLE ERROR: {e}"
                    should_stop = True    
                 
                except Exception as e:
                    tool_result = f"UNEXPECTED ERROR: {e}"
                    should_stop = True

            print(f"Tool Result: {tool_result}")

            if should_stop:
                break

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