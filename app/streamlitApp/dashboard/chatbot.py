import streamlit as st
from api.client import send_chat_message

def chatbot_page():
    st.subheader("💬 Course Chatbot")
    st.markdown("Ask questions about courses, syllabi, and class information!")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if question := st.chat_input("Ask about a course... (e.g., 'What are the topics in CIIC-4020?')"):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.write(question)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_chat_message(question)
                
                if "error" in response:
                    answer = f"Sorry, there was an error: {response['error']}"
                else:
                    answer = response.get("answer", "No response received")
                
                st.write(answer)
                
                # Add bot response to history
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()