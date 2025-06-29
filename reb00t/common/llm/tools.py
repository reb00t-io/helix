import json


tools_json = []
tools_python = []
tools_by_name = {}

def get_tools(pythonic=False):
    return tools_python if pythonic else tools_json

def add_tool(tool_json, tool_python, function):
    tools_by_name[tool_json["function"]["name"]] = function
    tools_json.append(tool_json)
    tools_python.append(tool_python)

def execute_tool(tool_call):
    name = tool_call.function.name
    if name not in tools_by_name:
        raise ValueError(f"Tool '{name}' not found.")

    fn = tools_by_name.get(name)
    args = tool_call.function.arguments

    # args can be a json string or dict
    if isinstance(args, str):
        args = json.loads(args)
    return fn(**args)
