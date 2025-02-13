import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
import io
import pandas as pd

# Initialize OpenAI client using Streamlit's secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Title of the app
st.title("Raj's ChatGPT App with Document Upload")

# Initialize session state for chat history and document content
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""

# File uploader for document upload
uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

# Function to extract text from documents
def extract_text_from_file(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            return "\n".join(para.text for para in doc.paragraphs)
        elif file_type == "text/plain":
            return uploaded_file.getvalue().decode("utf-8")
    return ""

# Extract and store document content
if uploaded_file:
    st.session_state.document_content = extract_text_from_file(uploaded_file)
    st.success("Document uploaded successfully!")

# Display chat history
for message in st.session_state.messages:
    role, content = message["role"], message["content"]
    with st.chat_message(role):
        st.markdown(content)

# Collect user input
user_input = st.chat_input("Type your message...")

# Function to get a response from OpenAI
def get_response(prompt):
    context = st.session_state.document_content[:2000]  # Limit to first 2000 chars
    full_prompt = f"Document Context:\n{context}\n\nUser Query: {prompt}"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant helping with document-based queries."},
            {"role": "user", "content": full_prompt}
        ]
    )
    return response.choices[0].message.content

# Function to format response into a table
def format_response_to_table(response):
    data = {
        "Field": [
            "Project Name", "Project overview", "Over All Team split", "Full-time employees", 
            "Contractor resources", "Skills used", "Project Scope", "Consultant contribution", 
            "Impact on the client/organization", "Challenges faced", "Project roadmap"
        ],
        "Details": response.split("\n")
    }
    return pd.DataFrame(data)

# Process and display response if there's input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant's response
    assistant_response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Format and display the response in a table
    response_table = format_response_to_table(assistant_response)
    st.table(response_table)