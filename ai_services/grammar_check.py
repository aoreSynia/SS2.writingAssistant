import os
import google.generativeai as genai

def check_grammar(content):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([f"Check the following text for grammar and spelling errors and return the errors in a list followed by the corrected text.\nText:\n{content}\n\nFormat:\nErrors:\n- [error1]\n- [error2]\n...\nCorrected Text:\n[corrected text]"])
    
    generated_text = response.candidates[0].content.parts[0].text
    
    if "\nCorrected Text:\n" not in generated_text:
        # Log the unexpected response format for debugging
        print(f"Unexpected response format: {generated_text}")
        return {
            "errors": [],
            "corrected_text": "Unable to parse response. Please try again."
        }
    
    try:
        errors_section, corrected_text_section = generated_text.split("\nCorrected Text:\n")
        errors = errors_section.split("\nErrors:\n")[1].strip().split("\n- ")
        errors = [error for error in errors if error]  # Remove any empty strings
        corrected_text = corrected_text_section.strip()
    except (IndexError, ValueError) as e:
        # Log the exception and the response for debugging
        print(f"Error parsing response: {e}")
        print(f"Response text: {generated_text}")
        return {
            "errors": [],
            "corrected_text": "Unable to parse response. Please try again."
        }
    
    return {
        "errors": errors,
        "corrected_text": corrected_text
    }
