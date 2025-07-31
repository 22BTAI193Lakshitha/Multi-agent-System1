from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import streamlit as st

class BaseAgent(ABC):
    def __init__(self, name: str, client, state_manager):
        self.name = name
        self.client = client
        self.state_manager = state_manager
        self.capabilities = []
    
    @abstractmethod
    def can_handle(self, input_type: str, has_image: bool = False) -> bool:
        """Determine if this agent can handle the given input type"""
        pass
    
    @abstractmethod
    def process(self, user_input: str, image_data: Optional[Any] = None) -> str:
        """Process the user input and return response"""
        pass
    
    def get_capabilities(self) -> list:
        """Return list of agent capabilities"""
        return self.capabilities
    
    def log_action(self, action: str, details: str = ""):
        """Log agent action"""
        st.write(f"🤖 **{self.name}**: {action}")
        if details:
            st.write(f"   *{details}*")
    
    def update_state(self, state_data: Dict[str, Any]):
        """Update agent's state"""
        self.state_manager.update_agent_state(self.name.lower().replace(' ', '_'), state_data)
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent's current state"""
        return self.state_manager.get_agent_state(self.name.lower().replace(' ', '_'))