

import os
import json
import re
import google.generativeai as genai

# Load prompts from JSON file
with open('prompts/prompt.json', 'r') as file:
    prompts = json.load(file)

def configure_genai(api_key):
    genai.configure(api_key=api_key)

def grammar_check( text):
    prompt_template = prompts['grammar_check']
    prompt = prompt_template['prompt'].replace("{{text}}", text)
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text
    
    # Parse response based on outputParsingPattern and outputParsingReplacement
    pattern = re.compile(prompt_template['outputParsingPattern'])
    matches = pattern.findall(generated_text)
    parsed_data = []
    for match in matches:
        parsed_item = {}
        for key, value in prompt_template['outputParsingReplacement'].items():
            parsed_item[key] = match[int(value.replace("$", "")) - 1]
        parsed_data.append(parsed_item)
    return {"highlighted_text": text, "parsed_data": parsed_data}



def check_plagiarism(text):
    prompt_template = prompts['plagiarism_check']
    prompt = prompt_template['prompt'].replace("{{text}}", text)
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text
    
    # Debugging print to check the response format
    print("Generated Text:", generated_text)

    # Parse response based on outputParsingPattern and outputParsingReplacement
    pattern = re.compile(prompt_template['outputParsingPattern'])
    matches = pattern.findall(generated_text)
    
    # Debugging print to check regex matches
    print("Matches:", matches)
    
    parsed_data = []
    for match in matches:
        parsed_item = {}
        for key, value in prompt_template['outputParsingReplacement'].items():
            parsed_item[key] = match[int(value.replace("$", "")) - 1]
        parsed_data.append(parsed_item)
    
    return {"highlighted_text": text, "parsed_data": parsed_data}



def complete_text(text):
    prompt_template = prompts['text_completion']
    prompt = prompt_template['prompt'].replace("{{incomplete_text}}", text)
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text

    return {"completed_text": generated_text}

def paraphrase_text(text):
    prompt_template = prompts['paraphrasing']
    prompt = prompt_template['prompt'].replace("{{text}}", text)
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text

    # Debugging print to check the response format
    print("Generated Text:", generated_text)

    return {"completed_text": generated_text}
