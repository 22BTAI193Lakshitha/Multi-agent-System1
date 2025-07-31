import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load the .env file
load_dotenv()

class GeminiClient:
    def __init__(self):
        # Load API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("Gemini API key not found. Please set GEMINI_API_KEY in the .env file.")
            st.stop()
        
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)

        # Initialize models
        
        self.text_model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        self.vision_model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    
    def generate_text_response(self, prompt, context=""):
        try:
            full_prompt = f"Context: {context}\n\nQuery: {prompt}" if context else prompt
            response = self.text_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating text response: {str(e)}"
    
    def generate_vision_response(self, prompt, image, context=""):
        try:
            full_prompt = f"Context: {context}\n\nQuery: {prompt}" if context else prompt
            response = self.vision_model.generate_content([full_prompt, image])
            return response.text
        except Exception as e:
            return f"Error generating vision response: {str(e)}"
