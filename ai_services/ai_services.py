from ntpath import join
import os
import json
import re
import google.generativeai as genai

# Load prompts from JSON file
with open('prompts/prompt.json', 'r') as file:
    prompts = json.load(file)

def configure_genai(api_key):
    genai.configure(api_key=api_key)

# Call API and get the result
def generate_content(prompt_type, text):
    prompt_template = prompts[prompt_type]
    prompt = prompt_template['prompt'].replace("@docs{{text}}", text)

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    generated_text = response.candidates[0].content.parts[0].text
    print("generated_text: {", generated_text , "}")
    return generated_text

# Grammar check function
def grammar_check(text):
    output = generate_content('grammar_check', text)
    print("input text: ", text)


    # Calculate positions of words in the original text
    original_words = text.split()
    corrected_words = output.split()

    positions = []
    current_pos = 0

    for word in original_words:
        start = text.find(word, current_pos)
        end = start + len(word)
        positions.append((start, end))
        current_pos = end + 1  # Skip the space between words

    # Find differences and prepare the result
    results = []
    for i, (orig_word, corr_word) in enumerate(zip(original_words, corrected_words)):
        if orig_word != corr_word:
            start, end = positions[i]
            results.append({
                "start": start,
                "end": end,
                "incorrect": orig_word,
                "suggestion": corr_word
            })

    print("results: ", results)
    return json.dumps({"errors": results}, ensure_ascii=False)

# Check plagiarism function
def check_plagiarism(text):
    generated_text = generate_content('plagiarism_check', text)
    pattern = prompts['plagiarism_check']['outputParsingPattern']
    replacements = prompts['plagiarism_check']['outputParsingReplacement']
    
    compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
    matches = compiled_pattern.findall(generated_text)

    parsed_data = []
    for match in matches:
        parsed_item = {}
        for key, value in replacements.items():
            parsed_item[key] = match[int(value.replace("$", "")) - 1]
        parsed_data.append(parsed_item)

    return {"highlighted_text": text, "parsed_data": parsed_data}

# Complete text function
def complete_text(text):
    generated_text = generate_content('text_completion', text)
    return {"completed_text": generated_text}

# Paraphrase text function
def paraphrase_text(text):
    generated_text = generate_content('paraphrasing', text)
    return {"paraphrased_text": generated_text}

# Example usage for grammar check
if __name__ == "__main__":
    sample_text = "After he arrived home, him and his brother went to the store to buy groceries. him is good with that."
    api_key = "your_api_key_here"
    configure_genai(api_key)

    result = grammar_check(sample_text)
    print(result)
