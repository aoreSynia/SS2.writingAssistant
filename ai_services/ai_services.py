import os
import json
import re
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load prompts from JSON file
with open('prompts/prompt.json', 'r') as file:
    prompts = json.load(file)

def configure_genai(api_key):
    genai.configure(api_key=api_key)

def generate_response(prompt_key, text):
    prompt_template = prompts[prompt_key]
    prompt = prompt_template['prompt'].replace("{{text}}", text)
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text
    
    # Parse response based on outputParsingPattern and outputParsingReplacement
    pattern = re.compile(prompt_template['outputParsingPattern'])
    matches = pattern.findall(generated_text)
    errors = []
    for match in matches:
        error = {}
        for key, value in prompt_template['outputParsingReplacement'].items():
            error[key] = match[int(value.replace("$", "")) - 1]
        errors.append(error)
    return {"highlighted_text": text, "errors": errors}


def grammar_check(text):
    result = generate_response("grammar_check", text)
    return result 


def check_plagiarism(text):
    result = generate_response("plagiarism_check", text)
    return result


def complete_text(text):
    result = generate_response("text_completion", text)
    return result


def paraphrase_text(text):
    result = generate_response("paraphrasing", text)
    return result

