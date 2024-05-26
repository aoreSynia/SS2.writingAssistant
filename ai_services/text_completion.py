import google.generativeai as genai
import os

def complete_text(content):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(["Continue the following text:", content])
    
    generated_text = response.candidates[0].content.parts[0].text
    return generated_text
