from .base_agent import BaseAgent
from .text_agent import TextAgent
from .vision_agent import VisionAgent
from typing import Any, Optional, List
import streamlit as st

class CoordinatorAgent(BaseAgent):
    def __init__(self, client, state_manager):
        super().__init__("Coordinator Agent", client, state_manager)
        self.text_agent = TextAgent(client, state_manager)
        self.vision_agent = VisionAgent(client, state_manager)
        self.capabilities = [
            "Route queries to appropriate agents",
            "Coordinate multi-agent responses",
            "Manage conversation flow",
            "Handle complex multi-modal inputs",
            "Maintain system state"
        ]
    
    def can_handle(self, input_type: str, has_image: bool = False) -> bool:
        """Coordinator can handle all types of inputs"""
        return True
    
    def process(self, user_input: str, image_data: Optional[Any] = None) -> str:
        """Coordinate processing between agents"""
        try:
            # Determine input characteristics
            has_image = image_data is not None
            input_type = self._determine_input_type(user_input, has_image)
            
            # Route to appropriate agent(s)
            response = self._route_request(user_input, image_data, input_type, has_image)
            
            # Update coordinator state
            self.update_state({
                'last_decision': input_type,
                'active': True,
                'last_routing': self._get_routing_info(input_type, has_image)
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Coordinator error: {str(e)}"
            self.update_state({'last_decision': 'error', 'active': False})
            return error_msg
    
    def _determine_input_type(self, user_input: str, has_image: bool) -> str:
        """Determine the type of input and processing needed"""
        if has_image:
            # Check if the text query is image-related
            image_keywords = ['image', 'picture', 'photo', 'see', 'look', 'visual', 'describe', 'analyze', 'identify', 'what is', 'what are']
            if any(keyword in user_input.lower() for keyword in image_keywords) or not user_input.strip():
                return "vision_primary"
            else:
                return "vision_with_text"
        else:
            return "text_only"
    
    def _route_request(self, user_input: str, image_data: Optional[Any], input_type: str, has_image: bool) -> str:
        """Route the request to appropriate agent(s)"""
        
        if input_type == "text_only":
            # Pure text processing
            self.log_action("Routing to Text Agent", "Processing text-only query")
            return self.text_agent.process(user_input, image_data)
        
        elif input_type == "vision_primary":
            # Image-focused processing
            self.log_action("Routing to Vision Agent", "Processing image-focused query")
            return self.vision_agent.process(user_input, image_data)
        
        elif input_type == "vision_with_text":
            # Multi-modal processing - both image and complex text
            self.log_action("Coordinating Multi-Modal Processing", "Using both Vision and Text agents")
            
            # First get vision analysis
            vision_response = self.vision_agent.process(user_input, image_data)
            
            # Then enhance with text processing if needed
            enhanced_query = f"Based on this image analysis: {vision_response}\n\nUser's additional question: {user_input}"
            text_response = self.text_agent.process(enhanced_query)
            
            # Combine responses intelligently
            combined_response = self._combine_responses(vision_response, text_response, user_input)
            return combined_response
        
        else:
            return "Unable to determine how to process this request."
    
    def _combine_responses(self, vision_response: str, text_response: str, original_query: str) -> str:
        """Combine vision and text responses intelligently"""
        # Use the coordinator's ability to synthesize responses
        synthesis_prompt = f"""
        Original user query: {original_query}
        
        Vision Agent Analysis: {vision_response}
        
        Text Agent Response: {text_response}
        
        Please provide a coherent, comprehensive response that combines the visual analysis with the textual reasoning to best answer the user's query.
        """
        
        try:
            synthesized = self.client.generate_text_response(synthesis_prompt)
            return f"**Comprehensive Analysis:**\n\n{synthesized}"
        except:
            # Fallback to simple combination
            return f"**Visual Analysis:**\n{vision_response}\n\n**Additional Analysis:**\n{text_response}"
    
    def _get_routing_info(self, input_type: str, has_image: bool) -> dict:
        """Get information about routing decision"""
        return {
            'input_type': input_type,
            'has_image': has_image,
            'agents_used': self._get_agents_used(input_type),
            'processing_mode': input_type
        }
    
    def _get_agents_used(self, input_type: str) -> List[str]:
        """Get list of agents used for processing"""
        if input_type == "text_only":
            return ["Text Agent"]
        elif input_type == "vision_primary":
            return ["Vision Agent"]
        elif input_type == "vision_with_text":
            return ["Vision Agent", "Text Agent"]
        else:
            return []
    
    def get_system_status(self) -> dict:
        """Get overall system status"""
        return {
            'coordinator': self.get_status(),
            'text_agent': self.text_agent.get_status(),
            'vision_agent': self.vision_agent.get_status(),
            'total_agents': 3,
            'active_agents': sum([
                1 if 'Active' in self.get_status() else 0,
                1 if 'Active' in self.text_agent.get_status() else 0,
                1 if 'Active' in self.vision_agent.get_status() else 0
            ])
        }
    
    def get_capabilities_summary(self) -> dict:
        """Get summary of all agent capabilities"""
        return {
            'coordinator': self.capabilities,
            'text_agent': self.text_agent.capabilities,
            'vision_agent': self.vision_agent.capabilities
        }
    
    def get_status(self) -> str:
        """Get coordinator status"""
        state = self.get_state()
        return "🟢 Active" if state.get('active', False) else "🔴 Inactive"