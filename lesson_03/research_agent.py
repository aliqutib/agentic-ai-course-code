"""
This file focus on creating a actual useful agent keeping in mind the next fundamental concept of planning, goal evaluation and agent trace
"""

from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OR_API_KEY")
)

conv_state = {
    "goal":None,
    "goal_achieved": False,
    "session": [{"role": "user", "content": "Research three open-source LLMs suitable for a low-resource machine, compare them, and prepare a recommendation"}],
    "action_history": [],
    "status": "running",
    "final_output": None,
    "step_count": 0,
    "retry_count": 0,
    "last_action": None,
    "last_result": None
}


conv_state["goal"] = conv_state["session"][0]["content"]

#------Planner-------

plan_state = {
    "goal": conv_state["goal"],
    "steps": [],
    "current_step": 0,
    "status": "not_started"
}

def create_plan(goal):

    response = client.chat.completions.create(
        model="qwen/qwen3-8b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a planning component. Break goals into short, "
                    "executable steps. Return only a JSON array of strings."
                )
            },
            {
                "role": "user",
                "content": goal
            }
        ]
    )

    steps = json.loads(response.choices[0].message.content)

    plan_state["steps"] = []

    for i, step in enumerate(steps):
        plan_state["steps"].append({
            "step_id": i + 1,
            "description": step,
            "status": "pending",
            "result": None
        })

    plan_state["status"] = "ready"

    return plan_state   

def get_current_step():
    index = plan_state["current_step"]

    if index >= len(plan_state["steps"]):
        return None

    return plan_state["steps"][index]

def complete_current_step(result):
    index = plan_state["current_step"]

    plan_state["steps"][index]["status"] = "completed"
    plan_state["steps"][index]["result"] = result

    plan_state["current_step"] += 1

    if plan_state["current_step"] >= len(plan_state["steps"]):
        plan_state["status"] = "completed"

def fail_current_step(error):
    index = plan_state["current_step"]

    plan_state["steps"][index]["status"] = "failed"
    plan_state["steps"][index]["result"] = error


#----Executer--------

tool_registry = {}

tool_schema= []

def execute(tool_name, arguments):

    if tool_name not in tool_registry:
        return {
            "success": False, 
            "error_type": "UNKNOWN_TOOL",
            "recoverable": False,
            "error": f"Unknown Tool: {tool_name}"}

    try:

        result = tool_registry[tool_name](**arguments)

        return {
            "success": True,
            "result": result
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
def is_valid_tool_call(tool_name, arguments):
    if tool_name in tool_registry.keys():
        for tool in tool_schema:
            if tool["function"]["name"]==tool_name:
                allowed_arguments = set(tool["function"]["parameters"]["properties"].keys())
                required_arguments = set(tool["function"]["required"])
                supplied_arguments = set(arguments.keys())
                if required_arguments.issubset(supplied_arguments) and supplied_arguments.issubset(allowed_arguments):
                    return {"valid": True, "Message": "Function and Arguments exsit in tool schema"}
                else:
                    return {"valid": False, "error_type": "INVALID_ARGUMENTS", "recoverable": True, "error": "Function exist but arguments are invalid"}
    else:
        return {"valid": False, "error_type": "UNKNOWN_TOOL", "recoverable": False, "error": "Function doesn't exist in tool schema"}
