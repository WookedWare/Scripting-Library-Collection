import openai
import time
from nltk.tokenize import sent_tokenize
import re

"""
Title: Easy Open AI
Author: WookedWare
Description: Provides functions to trim interact with OpenAI's api easier
Version: 1.0
"""

# Instructions for different methods
INSTRUCTIONS = {
    "default": "You are a helpful and intelligent assistant",
    "short": "You are a helpful and intelligent assistant who answers in very short and to the point answers",
    "long": "You are a helpful and intelligent assistant who answers in extremely long and thought out answers",
    "yesno": "You are an assistant that answers 'Yes', 'No', or 'Unknown' based on factual information. Please ensure your responses are accurate and aligned with known facts.",
    "one": "You are an assistant that must respond with only one word, no more, no less. Do not provide any additional context, explanation, or complete sentences. Only one word is allowed in your response.",
    "api": "You are an assistant that provides responses in concise JSON-like key-value pairs. Please respond to the user's queries with specific keys and values. For example, if asked about a famous show and its main actor, respond with: {'show': 'Name of the Show', 'actor': 'Name of the Actor'}.",
    "code": "You are an assistant that responds exclusively with executable code. The code must be in the language specified in the question, such as Bash, Python, Batch, or other programming languages. Your response must contain only the code itself, without any explanations, examples, or placeholders. Ensure that the code is complete, accurate, and includes all the logic requested. Do not include any comments or annotations within the code."
}

# Default options
DEFAULTS = {
    "endpoint": "chat",
    "temperature": 1.0,
    "top_p": 1.0,
    "max_length": 4096,
    "frequency_penalty": 1,
    "presence_penalty": 1
}

# Functions
def api_key_set(key):
    openai.api_key = key

def get_instruction(method, system_instruction=None):
    return INSTRUCTIONS.get(method, system_instruction or "You are a helpful assistant.")

def get_defaults(method, temperature, top_p):
    if method in ["api", "yesno"]:
        return {
            "temperature": temperature or 0.2,
            "top_p": top_p or 0.1
        }
    return {
        "temperature": temperature or DEFAULTS["temperature"],
        "top_p": top_p or DEFAULTS["top_p"]
    }

def conversation_start(model, endpoint=None, method=None, **kwargs):
    instruction = get_instruction(method, kwargs.get('system_instruction'))
    defaults = get_defaults(method, kwargs.get('temperature'), kwargs.get('top_p'))

    payload = {
        "temperature": defaults["temperature"],
        "top_p": defaults["top_p"],
        "frequency_penalty": kwargs.get('frequency_penalty', DEFAULTS["frequency_penalty"]),
        "presence_penalty": kwargs.get('presence_penalty', DEFAULTS["presence_penalty"])
    }

    conversation = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    return {
        "model": model,
        "endpoint": endpoint or DEFAULTS["endpoint"],
        "payload": payload,
        "conversation": conversation,
        "max_length": kwargs.get('max_length', DEFAULTS["max_length"]),
        "method": method
    }

def message_send(conversation, message):
    # Extract conversation details
    model, endpoint, payload, max_length, method, conversation_history = (
        conversation["model"],
        conversation["endpoint"],
        conversation["payload"],
        conversation["max_length"],
        conversation["method"],
        conversation["conversation"],
    )

    sentences = sent_tokenize(message)
    chunks = [sentence for sentence in sentences if len(sentence) <= max_length]

    response_content = None
    wait_time = 1
    max_retries = 3

    for chunk in chunks:
        conversation_chunk = {
            "role": "user",
            "content": chunk
        }
        conversation_history.append(conversation_chunk)

        payload["messages"] = conversation_history

        response_content = send_request(endpoint, model, payload, max_retries, wait_time)

        conversation_chunk = {
            "role": "assistant",
            "content": response_content
        }
        conversation_history.append(conversation_chunk)

    result = process_response(method, response_content)

    return {
        "conversation": conversation_history,
        "response": result,
    }

def send_request(endpoint, model, payload, max_retries, wait_time):
    for attempt in range(max_retries):
        try:
            if endpoint == "chat":
                response = openai.ChatCompletion.create(model=model, **payload)
            elif endpoint == "completions":
                response = openai.Completion.create(model=model, **payload)
            break
        except openai.error.OpenAIError as e:
            if hasattr(e, 'status_code') and e.status_code == 429:  # Rate limit error
                time.sleep(wait_time)
                wait_time *= 2
            else:
                raise e
    else:
        raise Exception("Max retries reached")

    return response.choices[0].message['content'] if endpoint == "chat" else response.choices[0].text

def process_response(method, response_content):
    if method == "api":
        keys_values = re.findall(r"'(\w+)': '([^']+)'", response_content)
        return {key: value for key, value in keys_values}
    elif method == "yesno":
        return "Yes" if "Yes" in response_content else "No" if "No" in response_content else "Unknown"
    else:
        return response_content

def message_send_single(model, message, **kwargs):
    conversation = conversation_start(model, **kwargs)
    return message_send(conversation, message)["response"]
