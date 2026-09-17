import os
import json

from openai import OpenAI
from dotenv import load_dotenv

task_list = [{'task_id': 'TASK-1', 'task_title': 'Learn tool calling', 'task_description': 'Connect OpenRouter to our agent', 'priority': 'high', 'completed': False}]
task_id_num = 0 

def create_task(task_title, task_description, priority="medium"):
    global task_id_num
    task_id_num += 1
    task = {"task_id": f"TASK-{task_id_num}", "task_title": task_title, "task_description": task_description, "priority": priority, "completed": False}
    task_list.append(task)
    return task

def search_tasks(query):
    query = query.lower()

    return [
        task for task in task_list
        if query in task["task_id"].lower()
        or query in task["task_title"].lower()
        or query in task["task_description"].lower()
        or query in task["priority"].lower()
    ]

def mark_as_completed(task_id):
    for task in task_list:
        if task["task_id"] == task_id:
            task["completed"] = True
            return task 
    else:
        return {"error": "Task not found"}


tool_schema = [
    {
        "type":"function",
        "function":{
            "name": "create_task",
            "description": "A tool to create/add task in the rest of task list for the user",
            "parameters":{
                "type": "object",
                "properties": {
                    "task_title":{
                        "type": "string",
                        "description":"Task title to be shown as heading - max 50 character"
                    },
                    "task_description": {
                        "type": "string",
                        "description":"Detailed description of the task - max 500 characters"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "based on the description priority flag to the task",
                        "default": "medium"
                    }
                }
            },
            "required": ["task_title"]
        }
    },
    {
        "type":"function",
        "function":{
            "name": "search_tasks",
            "description": "A tool to return sublist of the task which match query",
            "parameters":{
                "type": "object",
                "properties": {
                    "query":{
                        "type": "string",
                        "description":"phrase mentioning task\'s id, title, description or priority flag which is supposed to be matched"
                    }
                }
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name": "mark_as_completed",
            "description": "A tool to mark any task completed",
            "parameters":{
                "type": "object",
                "properties": {
                    "task_id":{
                        "type": "string",
                        "description":"Unique task id which helps to find specific task from the list"
                    },
                }
            }
        }
    }
]


#___________TOOL ENDS_________

tool_registry = {"create_task": create_task, "search_tasks": search_tasks, "mark_as_completed": mark_as_completed}

def execute(tool_name, arguements):

    if tool_name not in tool_registry:
        return {"Error": f"Unknown Tool: {tool_name}"}

    return tool_registry[tool_name](**arguements)


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OR_API_KEY")
)

session = [{"role": "user", "content": "Find my task related to tool calling and mark it as completed."}]

MAX_ITERATION = 5

for _ in range(MAX_ITERATION):

    response = client.chat.completions.create(
        model="qwen/qwen3-8b",
        messages=session,
        tools=tool_schema
    )

    message = response.choices[0].message
    session.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguements = json.loads(tool_call.function.arguments)
            tool_result = execute(tool_name=tool_name, arguements=arguements)
            session.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
    else:
        print(f"Final Answer: {message.content}")
        break

print(session)