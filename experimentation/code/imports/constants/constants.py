TOOL_USE_COMPLETION_DESCRIPTION_FORMAT = \
    """
        The tool use output you give must follow the
        json format in the following form:

        {
            "<<function_name1>>": {
                "function_call_explanation": <function_call_explanation>
                "args":
                    {
                        "<<arg_name1>>": "<arg1_value>",
                        "<<arg_name2>>": "<arg2_value>",
                        ...
                        "<<arg_nameN>>": "<argn_value>"
                    },
            },
            <<function_name2>>: {
                "function_call_explanation": <function_call_explanation>,
                "args":
                    {
                        "<<arg_name1>>": "<arg1_value>",
                        "<<arg_name2>>": "<arg2_value>",
                        ...
                        "<<arg_nameN>>": "<argn_value>",
                    },
            ...
            <<function_nameN>>: {
                "function_call_explanation": <function_call_explanation>,
                "args":
                    {
                        "<<arg_name1>>": "<arg1_value>",
                        "<<arg_name2>>": "<arg2_value>",
                        ...
                        "<<arg_nameN>>": "<argn_value>",
                    }
            },
        }

        Where:
            -  < > denotes that whats inside of it is variable and you should 
        replace it with the actual value. 
            - << >> denotes that whats inside of it is variable and you should
            extract the value from the tools description provided to use
    """


SWE_BACKSTORY = "You are a Software Engineer that helps to \
resolve issues in a software development environment."