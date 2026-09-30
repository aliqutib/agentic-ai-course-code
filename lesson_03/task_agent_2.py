import os
import json

from openai import OpenAI
from dotenv import load_dotenv

task_list = [{'task_id': 'TASK-1', 'task_title': 'Learn tool calling', 'task_description': 'Connect OpenRouter to our agent', 'priority': 'high', 'completed': False}]
task_id_num = 0 

#------Exception------#

class TaskNotFoundError(Exception):
    pass

#---------------------#


def create_task(task_title, task_description, priority="medium"):
    global task_id_num
    task_id_num += 1
    task = {"task_id": f"TASK-{task_id_num}", "task_title": task_title, "task_description": task_description, "priority": priority, "completed": False}
    task_list.append(task)
    return task

def search_tasks(query):
    query = query.lower()

    found_tasks = [
        task for task in task_list
        if query in task["task_id"].lower()
        or query in task["task_title"].lower()
        or query in task["task_description"].lower()
        or query in task["priority"].lower()
    ]

    return found_tasks


def mark_as_completed(task_id):
    for task in task_list:
        if task["task_id"] == task_id:
            task["completed"] = True
            return task
    
    raise TaskNotFoundError(f"Task {task_id} was not found")


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
            },
            "required": ["query"]
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
            },
            "required": ["task_id"]
        }
    }
]


#___________TOOL ENDS_________

tool_registry = {"create_task": create_task, "search_tasks": search_tasks, "mark_as_completed": mark_as_completed}

#dispatcher
def execute(tool_name, arguements):

    if tool_name not in tool_registry:
        return {
            "success": False, 
            "error_type": "UNKNOWN_TOOL",
            "recoverable": False,
            "error": f"Unknown Tool: {tool_name}"}

    try:

        result = tool_registry[tool_name](**arguements)

        return {
            "success": True,
            "result": result
        }

    except TaskNotFoundError as e:
        return {
                "success": False,
                "error_type": "NOT_FOUND",
                "recoverable": True,
                "error": str(e)
            }

    except TypeError as e:
        return {
            "success": False,
            "error_type": "INVALID_ARGUMENTS",
            "recoverable": True,
            "error": str(e)
        }
    
    except Exception as e:

        return {
            "success": False,
            "error_type": "EXECUTION_ERROR",
            "recoverable": False,
            "error": str(e)
        }

#tool validator
def is_valid_tool_call(tool_name, arguements):
    if tool_name in tool_registry.keys():
        for tool in tool_schema:
            if tool["function"]["name"]==tool_name:
                allowed_arguements = set(tool["function"]["parameters"]["properties"].keys())
                required_arguements = set(tool["function"]["required"])
                supplied_arguements = set(arguements.keys())
                if required_arguements.issubset(supplied_arguements) and supplied_arguements.issubset(allowed_arguements):
                    return {"valid": True, "Message": "Function and Arguements exsit in tool schema"}
                else:
                    return {"valid": False, "error_type": "INVALID_ARGUMENTS", "recoverable": True, "error": "Function exist but arguements are invalid"}
    else:
        return {"valid": False, "error_type": "UNKNOWN_TOOL", "recoverable": False, "error": "Function doesn't exist in tool schema"}



#----Agent Logic-------

load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OR_API_KEY")
)



state = {
    "goal":None,
    "session": [{"role": "user", "content": "Find my task regarding creating space ship and mail its details to my personal email account"}],
    "status": "running",
    "final_output": None,
    "step_count": 0,
    "retry_count": 0,
    "last_action": None,
    "last_result": None
}

state["goal"] = state["session"][0]["content"]

MAX_ITERATION = 5
MAX_RETRIES = 2

while state["status"] == "running":

    if state["step_count"] >= MAX_ITERATION:
        state["status"] = "failed"
        state["final_output"] = "Agent Reached Maximum Iteration"
        break

    response = client.chat.completions.create(
        model="qwen/qwen3-8b",
        messages=state["session"],
        tools=tool_schema
    )

    state["step_count"] += 1


    message = response.choices[0].message
    state["session"].append(message) 

    if message.tool_calls:
        for tool_call in message.tool_calls:
            state["last_action"] = tool_call
            tool_name = tool_call.function.name
            arguements = json.loads(tool_call.function.arguments)

            validation = is_valid_tool_call(tool_name, arguements)

            if validation["valid"]:
                tool_result = execute(tool_name=tool_name, arguements=arguements)
            else:
                tool_result = validation
            
            if not tool_result.get("success", validation.get("valid", False)):
                if tool_result["recoverable"]:
                    state["retry_count"] += 1
                    if state["retry_count"] >= MAX_RETRIES:
                        state["status"] = "failed"
                        state["final_output"] = "Maximum recovery attempts reached"
                        break

                elif not tool_result["recoverable"]:
                    state["status"] = "failed"
                    state["final_output"] = f"Non-recoverable error: {tool_result['error']}"
                    break
                
            elif tool_result.get("success"):
                state["retry_count"] = 0

            state["last_result"] = tool_result
            state["session"].append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
    else:
        state["status"] = "completed"
        state["final_output"] = f"Final Answer: {message.content}"

print(state["final_output"])