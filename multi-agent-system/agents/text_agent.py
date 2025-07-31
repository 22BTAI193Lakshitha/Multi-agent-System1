from .base_agent import BaseAgent
from typing import Any, Optional
import streamlit as st

class TextAgent(BaseAgent):
    def __init__(self, client, state_manager):
        super().__init__("Text Agent", client, state_manager)
        self.capabilities = [
            "Answer general questions",
            "Provide explanations",
            "Generate text content",
            "Analyze text data",
            "Provide recommendations"
        ]
    
    def can_handle(self, input_type: str, has_image: bool = False) -> bool:
        """Text agent can handle text inputs and text-related queries"""
        return input_type == "text" and not has_image
    
    def process(self, user_input: str, image_data: Optional[Any] = None) -> str:
        """Process text input and generate response"""
        try:
            # Get conversation context for better responses
            context = self.state_manager.get_context()
            
            # Enhance prompt with context if available
            enhanced_prompt = self._enhance_prompt(user_input, context)
            
            # Generate response using Gemini
            response = self.client.generate_text_response(enhanced_prompt, context)
            
            # Update agent state
            self.update_state({'last_response': response, 'active': True})
            
            # Update conversation context
            self.state_manager.update_context(f"User asked: {user_input}\nAgent responded: {response[:200]}...")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing text input: {str(e)}"
            self.update_state({'last_response': error_msg, 'active': False})
            return error_msg
    
    def _enhance_prompt(self, user_input: str, context: str) -> str:
        """Enhance user prompt with additional context and instructions"""
        base_instruction = """You are a helpful AI assistant specializing in text-based interactions. 
        Provide clear, accurate, and contextually relevant responses. If you need more information to give a better answer, ask clarifying questions."""
        
        if context:
            enhanced = f"{base_instruction}\n\nConversation Context:\n{context}\n\nUser Query: {user_input}"
        else:
            enhanced = f"{base_instruction}\n\nUser Query: {user_input}"
        
        return enhanced
    
    def get_status(self) -> str:
        """Get current agent status"""
        state = self.get_state()
        return "🟢 Active" if state.get('active', False) else "🔴 Inactive"