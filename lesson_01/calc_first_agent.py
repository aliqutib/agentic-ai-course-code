#------utils----
def calculate(expression):
    return eval(expression)


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "A tool to calculate mathematical expression",
            "parameters":{
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string", 
                        "description": "A mathematical expression to calculate"
                    }
                }
            },
            "required": ["expression"]
        }
    }
]
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

session = [{"role": "user", "content": "What is 125 * 37"}]

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

            if tool_name == "calculator":
                tool_result = calculate(parameters["expression"])
            else:
                tool_result = f"Unknow tool: {tool_name}"

            print(f"Tool Result: {tool_result}")

            session.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_call_id": tool_call.id
            })

    else:

        print(f"Final Answer: {message.content}")

        break