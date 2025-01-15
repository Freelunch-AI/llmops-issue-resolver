import base64
import math
import os
import sys
from contextlib import contextmanager
from io import BytesIO
from typing import Optional

import requests
import tiktoken
from PIL import Image
from pydantic import ValidationError


@contextmanager
def temporary_sys_path(path):
    """
    A context manager to temporarily add a specified path to the system path.
    This context manager appends the given path to `sys.path` and ensures that 
    the original `sys.path` is restored after the context is exited.
    Args:
        path (str): The path to be temporarily added to `sys.path`.
    Yields:
        None: This context manager does not yield any value.
    Example:
        with temporary_sys_path('/some/path'):
            # Perform operations that require the temporary path
    """
    original_sys_path = sys.path.copy()
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = original_sys_path

# do some imports 'assuming' that the package is installed
# before: 'from agent import ..."
# now: "from llmops_issue_resolver.agent import ..."
# But why do this? 
#     - Because mypy assumes this notation when importing from modules within a package
#     - Because it makes it cleanar for doing imports within modules that are very deep 
#     and want to import from modules that are near surface of the package directory 
#     tree
# All .py modules need to have this line, but with the more general form of the import

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     '..', '..', '..', '..'))):
    from experimentation.code.imports.schemas.schema_models import (
        Message,
        Messages,
        StringModel,
    )
    
# assumes detail=high
def calculate_number_of_image_tokens(url: Optional[str] = None, \
                                     local_openai_image: Optional[str] = None) -> int:
    if url:
        response = requests.get(url)
        image_data = response.content
    else:
        # print("------------local_openai_image------------\n", local_openai_image)
        base64_image = local_openai_image.split(",")[1][2:-1]
        base64_image = base64_image
        image_data = base64.b64decode(base64_image)
        
    image = Image.open(BytesIO(image_data))
    width, height = image.size

    # detail: high
    if width > 2048 or height > 2048:
        scaling_factor = 2048 / max(width, height)
        width = int(width * scaling_factor)
        height = int(height * scaling_factor)

    scaling_factor = 768 / min(width, height)
    width = int(width * scaling_factor)
    height = int(height * scaling_factor)

    num_tiles = math.ceil(width / 512) * math.ceil(height / 512)
    num_tokens = 170 * num_tiles + 85
    return num_tokens

def calculate_number_of_tokens(messages: Messages, tokenization_method: str) -> int:
    """Calculates the number of tokens in a list of messages.

    Args:
        messages (Messages): The list of OpenAI messages.

    Returns:
        int: The number of tokens in the list of OpenAI messages.
    """

    try:
        Messages(messages=messages)
        StringModel(items=tokenization_method)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError

    encoding = tiktoken.get_encoding(tokenization_method)

    text = ""
    url_images = []
    local_openai_images = []
    for message in messages:
        if isinstance(message, Message):
            text += message.content
        else:
            for item in message.content:
                if 'text' in item:
                    text += item['text']
                else:
                    image = item['image_url']['url']

                    # check if its an image url or base64 image
                    if image.startswith("http"):
                        url_images.append(image)
                    else:
                        local_openai_images.append(image)

    #calculate numerb of text tokens
    text_number_of_tokens = len(encoding.encode(text))

    # calculate number of url_images tokens
    url_images_number_of_tokens = sum(calculate_number_of_image_tokens(url=url) 
                                      for url in url_images)
    # calculate number of base64_images tokens
    local_images_number_of_tokens = \
        sum(calculate_number_of_image_tokens(local_openai_image=local_openai_image) \
            for local_openai_image in local_openai_images)

    # sum all the tokens
    number_of_tokens = text_number_of_tokens + url_images_number_of_tokens + \
        local_images_number_of_tokens

    return number_of_tokens