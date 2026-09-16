def calculate(expression):
    return eval(expression)

def get_tools():
    calculator_tool = {
        "name": "calculator",
        "description": "A tool to calculate mathematical expression",
        "parameters": 
                {
                    "expression": {
                        "type": "string",
                        "description": "string consist of mathematical expression"
                    }
                }   
        
    }

    return [calculator_tool]

def agent_loop():

    user_input = input("Enter input: ")
    session = [{"user": user_input}]
    
    internal_state = LLM(session) #state can be {action: "tool", tool_name:"calculator", parameters: expression}

    
    while True:    

        if internal_state.action == "tool":
            tool_result = execute_tool(internal_state.tool_name, internal_state.parameters)
            session.append({"LLM": internal_state, "Tool Result": tool_result})
        elif internal_state.action == "final_answer":
            return internal_state

        internal_state = LLM(session)



schema = [
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
            "name": "complete_task",
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
        
            
