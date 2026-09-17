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

        
            
