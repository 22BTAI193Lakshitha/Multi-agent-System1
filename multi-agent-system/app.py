import os
from dotenv import load_dotenv

import streamlit as st
import os
from PIL import Image
import io

# Import our custom modules
from utils.gemini_client import GeminiClient
from utils.state_manager import StateManager
from agents.coordinator_agent import CoordinatorAgent

# Page configuration
st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_system():
    """Initialize the multi-agent system"""
    if 'system_initialized' not in st.session_state:
        try:
            # Initialize components
            st.session_state.gemini_client = GeminiClient()
            st.session_state.state_manager = StateManager()
            st.session_state.coordinator = CoordinatorAgent(
                st.session_state.gemini_client,
                st.session_state.state_manager
            )
            st.session_state.system_initialized = True
        except Exception as e:
            st.error(f"Failed to initialize system: {str(e)}")
            st.stop()

def display_header():
    """Display the application header"""
    st.title("🤖 Multi-Agent AI System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**An intelligent system that handles both text and image inputs using specialized agents**")
    with col2:
        if st.button("🗑️ Clear History", help="Clear conversation history"):
            st.session_state.state_manager.clear_history()
            st.rerun()
    with col3:
        st.markdown(f"**Messages:** {len(st.session_state.state_manager.get_recent_history(1000))}")

def display_sidebar():
    """Display sidebar with system information"""
    with st.sidebar:
        st.header("📊 System Status")
        
        # Get system status
        coordinator = st.session_state.coordinator
        status = coordinator.get_system_status()
        
        # Display agent status
        st.subheader("🤖 Agents")
        st.write(f"**Coordinator:** {status['coordinator']}")
        st.write(f"**Text Agent:** {status['text_agent']}")
        st.write(f"**Vision Agent:** {status['vision_agent']}")
        
        st.markdown("---")
        
        # Display capabilities
        st.subheader("⚡ Capabilities")
        capabilities = coordinator.get_capabilities_summary()
        
        with st.expander("📝 Text Agent"):
            for cap in capabilities['text_agent']:
                st.write(f"• {cap}")
        
        with st.expander("👁️ Vision Agent"):
            for cap in capabilities['vision_agent']:
                st.write(f"• {cap}")
        
        with st.expander("🎯 Coordinator"):
            for cap in capabilities['coordinator']:
                st.write(f"• {cap}")
        
        st.markdown("---")
        
        # Display recent context
        st.subheader("💭 Context")
        context = st.session_state.state_manager.get_context()
        if context:
            st.text_area("Current Context", context, height=100, disabled=True)
        else:
            st.write("*No context available*")

def display_conversation_history():
    """Display conversation history"""
    history = st.session_state.state_manager.get_recent_history(10)
    
    if history:
        st.subheader("💬 Recent Conversation")
        
        for i, interaction in enumerate(reversed(history)):
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(f"**{interaction['agent_type']}**")
                    if interaction['has_image']:
                        st.write("🖼️ *With Image*")
                
                with col2:
                    st.write(f"**User:** {interaction['user_input']}")
                    st.write(f"**Response:** {interaction['agent_response'][:200]}...")
                
                st.markdown("---")

def handle_user_input():
    """Handle user input processing"""
    coordinator = st.session_state.coordinator
    state_manager = st.session_state.state_manager
    
    # Create input section
    st.subheader("💭 Ask Me Anything")
    
    # File uploader for images
    uploaded_file = st.file_uploader(
        "Upload an image (optional)",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        help="Upload an image for visual analysis"
    )
    
    # Text input
    user_input = st.text_area(
        "Your question or message:",
        placeholder="Ask about the image, request analysis, or ask any question...",
        height=100
    )
    
    # Process button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        process_button = st.button("🚀 Process", type="primary")
    with col2:
        if st.button("🔄 Reset Input"):
            st.rerun()
    
    # Handle processing
    if process_button and (user_input.strip() or uploaded_file):
        with st.spinner("🤖 Processing your request..."):
            try:
                # Process uploaded image
                image_data = None
                if uploaded_file:
                    image_data = Image.open(uploaded_file)
                    state_manager.add_uploaded_image(image_data)
                    
                    # Display uploaded image
                    st.image(image_data, caption="Uploaded Image")
                
                # Process the request
                response = coordinator.process(user_input, image_data)
                
                # Determine agent type used
                agent_type = "Coordinator"
                if hasattr(coordinator, 'get_state'):
                    state = coordinator.get_state()
                    last_decision = state.get('last_decision', '')
                    if 'text' in last_decision:
                        agent_type = "Text Agent"
                    elif 'vision' in last_decision:
                        agent_type = "Vision Agent"
                
                # Add to history
                state_manager.add_to_history(
                    user_input, 
                    response, 
                    agent_type, 
                    image_data
                )
                
                # Display response
                st.success("✅ Response Generated!")
                st.markdown("### 🤖 Agent Response:")
                st.markdown(response)
                
            except Exception as e:
                st.error(f"❌ Error processing request: {str(e)}")
    
    elif process_button:
        st.warning("⚠️ Please provide either text input or upload an image.")

def display_examples():
    """Display example queries"""
    with st.expander("💡 Example Queries"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Text Queries:**")
            st.markdown("• What is artificial intelligence?")
            st.markdown("• Explain quantum computing")
            st.markdown("• Write a Python function to sort a list")
            st.markdown("• What are the benefits of renewable energy?")
        
        with col2:
            st.markdown("**Image Queries:**")
            st.markdown("• What do you see in this image?")
            st.markdown("• Describe the colors and composition")
            st.markdown("• Identify objects in the picture")
            st.markdown("• Read any text visible in the image")

def main():
    """Main application function"""
    # Initialize system
    initialize_system()
    
    # Display header
    display_header()
    
    # Create main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Handle user input
        handle_user_input()
        
        # Display examples
        display_examples()
        
        # Display conversation history
        display_conversation_history()
    
    with col2:
        # Display sidebar content in the right column
        display_sidebar()

if __name__ == "__main__":
    main()