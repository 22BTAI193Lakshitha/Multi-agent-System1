import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional

class StateManager:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        
        if 'current_context' not in st.session_state:
            st.session_state.current_context = ""
        
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = []
        
        if 'agent_states' not in st.session_state:
            st.session_state.agent_states = {
                'text_agent': {'active': True, 'last_response': ''},
                'vision_agent': {'active': True, 'last_response': ''},
                'coordinator': {'active': True, 'last_decision': ''}
            }
    
    def add_to_history(self, user_input: str, agent_response: str, agent_type: str, image_data: Optional[Any] = None):
        """Add interaction to conversation history"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'agent_type': agent_type,
            'has_image': image_data is not None
        }
        st.session_state.conversation_history.append(interaction)
    
    def update_context(self, new_context: str):
        """Update current context with new information"""
        if st.session_state.current_context:
            st.session_state.current_context += f"\n{new_context}"
        else:
            st.session_state.current_context = new_context
        
        # Keep context manageable (last 1000 characters)
        if len(st.session_state.current_context) > 1000:
            st.session_state.current_context = st.session_state.current_context[-1000:]
    
    def get_context(self) -> str:
        """Get current conversation context"""
        return st.session_state.current_context
    
    def get_recent_history(self, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        return st.session_state.conversation_history[-limit:] if st.session_state.conversation_history else []
    
    def clear_history(self):
        """Clear conversation history and context"""
        st.session_state.conversation_history = []
        st.session_state.current_context = ""
        st.session_state.uploaded_images = []
    
    def update_agent_state(self, agent_name: str, state_data: Dict[str, Any]):
        """Update specific agent state"""
        if agent_name in st.session_state.agent_states:
            st.session_state.agent_states[agent_name].update(state_data)
    
    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get specific agent state"""
        return st.session_state.agent_states.get(agent_name, {})
    
    def add_uploaded_image(self, image_data: Any):
        """Add uploaded image to state"""
        st.session_state.uploaded_images.append({
            'timestamp': datetime.now().isoformat(),
            'image': image_data
        })
    
    def get_latest_image(self) -> Optional[Any]:
        """Get the most recently uploaded image"""
        if st.session_state.uploaded_images:
            return st.session_state.uploaded_images[-1]['image']
        return None