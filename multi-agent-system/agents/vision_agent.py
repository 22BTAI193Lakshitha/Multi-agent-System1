from .base_agent import BaseAgent
from typing import Any, Optional
import streamlit as st
from PIL import Image

class VisionAgent(BaseAgent):
    def __init__(self, client, state_manager):
        super().__init__("Vision Agent", client, state_manager)
        self.capabilities = [
            "Analyze images and photos",
            "Answer questions about visual content",
            "Describe image contents",
            "Identify objects, people, and scenes",
            "Read text from images (OCR)",
            "Compare multiple images"
        ]
    
    def can_handle(self, input_type: str, has_image: bool = False) -> bool:
        """Vision agent handles inputs with images"""
        return has_image or input_type == "image"
    
    def process(self, user_input: str, image_data: Optional[Any] = None) -> str:
        """Process image input and generate response"""
        try:
            if image_data is None:
                # Try to get the latest uploaded image
                image_data = self.state_manager.get_latest_image()
                
            if image_data is None:
                return "No image provided. Please upload an image for visual analysis."
            
            # Get conversation context
            context = self.state_manager.get_context()
            
            # Enhance prompt for vision tasks
            enhanced_prompt = self._enhance_vision_prompt(user_input, context)
            
            # Process image - ensure it's in correct format
            processed_image = self._process_image(image_data)
            
            # Generate response using Gemini Vision
            response = self.client.generate_vision_response(enhanced_prompt, processed_image, context)
            
            # Update agent state
            self.update_state({'last_response': response, 'active': True})
            
            # Update conversation context
            self.state_manager.update_context(f"User asked about image: {user_input}\nVision analysis: {response[:200]}...")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            self.update_state({'last_response': error_msg, 'active': False})
            return error_msg
    
    def _enhance_vision_prompt(self, user_input: str, context: str) -> str:
        """Enhance user prompt for vision-specific tasks"""
        base_instruction = """You are a specialized vision AI assistant. Analyze the provided image carefully and respond to the user's query with detailed, accurate observations. 
        Focus on visual elements, objects, people, text, colors, composition, and any relevant details that address the user's question."""
        
        if not user_input.strip():
            user_input = "Please describe this image in detail."
        
        if context:
            enhanced = f"{base_instruction}\n\nConversation Context:\n{context}\n\nUser Query about the image: {user_input}"
        else:
            enhanced = f"{base_instruction}\n\nUser Query about the image: {user_input}"
        
        return enhanced
    
    def _process_image(self, image_data: Any) -> Any:
        """Process image data to ensure it's in the correct format for Gemini"""
        try:
            if isinstance(image_data, Image.Image):
                return image_data
            elif hasattr(image_data, 'read'):
                # It's a file-like object
                return Image.open(image_data)
            else:
                # Assume it's already processed
                return image_data
        except Exception as e:
            raise Exception(f"Unable to process image: {str(e)}")
    
    def get_status(self) -> str:
        """Get current agent status"""
        state = self.get_state()
        return "🟢 Active" if state.get('active', False) else "🔴 Inactive"
    
    def analyze_image_content(self, image_data: Any) -> str:
        """Perform general image analysis"""
        return self.process("Provide a comprehensive analysis of this image, including objects, people, setting, colors, and overall composition.", image_data)