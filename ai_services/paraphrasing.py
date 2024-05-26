import google.generativeai as genai
import os

def paraphrase_text(content):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(["Paraphrase the following text:", content])
    
    generated_text = response.candidates[0].content.parts[0].text
    return generated_text
