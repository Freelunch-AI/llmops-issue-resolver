TEXT_TO_CONTEXT_OVERLOAD = "Hello" * 128001

SWE_BACKSTORY = "You are a Software Engineer that helps to \
resolve issues in a software development environment."

DOCS_ALL = { 
    "get_directory_tree": {
        "summary_of_the_tool": {
            "what_you_want_to_do": "Get the directory tree of the given path up \
                until depth=2", 
            "how_to_do_it": "get_directory_tree(path='/path/to/directory', depth=2)",
            "required_parameters": [{
                "name": "path",
                "type": "str",
                "description": """The path to the directory to get
                    the directory tree from
                """
            }],
            "optional_config_parameters": [{
                "name": "depth",
                "type": "str",
                "description": """
                    The maximum number of subdirectory levels to show. E.g., 
                    'path/to/dir has 2 levels of directory depth
                """
            }],
            "tips_on_when_to_do_it": """
                When you want to understand the structure of 
                a repo or search for specific types of files
            """, 
            "tips_on_when_not_to_do_it": """
                when you need to find a specific file 
                or matching pattern in the entire repo, then you should use a search
                tool gving the file name, file extension extension or pattern 
                you are looking for.
            """
        },
        "examples_of_the_tool_being_used": [
            {
                "situation": """You want to get an inital feeling about the structure 
                    of a complex repository to start understanding how it works""", 
                "tool_use_in_english": """Get the directory tree of the root 
                    directory up until 5 levels of depth""", 
                "tool_use": "get_directory_tree(path='/', depth=2)", 
                "parameters_choice_explanation": """5 levels of depth is 
                    probably enough 
                    to get a initial good understanding of the structure of the 
                    repository, \since the most relevant stuff will probably be under 
                    src/<package_name> . If its way less than 5 you want get a good 
                    picture of the core subfolders and files. if its way more than 5 
                    it can be too much detail not necesssary at this stage which makes 
                    it harder to get a high-level understanding. If you use this 
                    tool with depth=5 and you see that you are missing some important
                    things, you can always go deeper with a higher depth, 
                    its an iterative process.""",
                "exceptions_to_the_parameters_choice_explanation": """
                    There are very complex repositories that have an 
                    extensive hierarchical structure. In these cases you should go 
                    deeper, and use more depth. How to know when to go deeper?
                    Generally you either will see that you are missing some important
                    things in a previous use of this tool or you can use another tool
                    before to check the avarage depth of files or other similar metric
                    that gives you an idea of the complexity of the repository.
                """
            }
        ]
    }
}

COST_MAPPING_1M_TOKENS = {
            "gpt-4o-mini": {
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                },
                "context_window": 128000,
                "max_output_tokens": 16384,
                "tokenization_method": "o200k_base"
            },
            "gpt-4o": { # prices are not real
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                },
                "context_window": 128000,
                "max_output_tokens": 16384,
                "tokenization_method": "o200k_base"
            },
            "gpt-4": { # prices are not real
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                },
                "context_window": 8192,
                "max_output_tokens": 8192,
                "tokenization_method": "cl100k_base"
            }
        }
