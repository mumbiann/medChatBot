import streamlit as st
import pdfplumber
import openai
import os

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to extract text from PDF in chunks
def extract_text_chunks(pdf_file, chunk_size=1000):
    text_chunks = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
                text_chunks.extend(chunks)
    return text_chunks

# Function to generate responses using OpenAI's chat models
def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the chat model
        messages=messages,
        max_tokens=150
    )
    return response.choices[0].message['content'].strip()

# Streamlit UI
st.set_page_config(layout="wide")  # Set page layout to wide

# Header
st.title("Maternal Health Document Analyzer")
st.markdown("---")

# Sidebar
st.sidebar.title("Settings")
uploaded_files = st.sidebar.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
question = st.sidebar.text_input("Ask a question about the documents:")
st.sidebar.markdown("---")

# Main content area
col1, col2 = st.columns([1, 3])

all_text_chunks = []

with col1:
    if uploaded_files:
        st.subheader("Extracted Text Chunks")
        for uploaded_file in uploaded_files:
            st.markdown(f"**{uploaded_file.name}**")
            with st.spinner(f'Extracting text from {uploaded_file.name}...'):
                text_chunks = extract_text_chunks(uploaded_file)
                all_text_chunks.extend(text_chunks)
            for i, chunk in enumerate(text_chunks):
                st.write(f"Chunk {i + 1}:")
                st.write(chunk)

with col2:
    if question and all_text_chunks:
        combined_text = " ".join(all_text_chunks)
        messages = [
            {"role": "system", "content": "You are a maternal health assistant."},
            {"role": "user", "content": f"The following is the content of several documents:\n{combined_text}\n\nQuestion: {question}"}
        ]
        if st.button("Get Answer", key="get-answer"):
            with st.spinner('Generating answer...'):
                response = generate_response(messages)
            st.subheader("AI Generated Answer")
            st.write(response)

# Footer
st.markdown("---")
st.info("This app is for educational purposes only.")


st.markdown(
    """
    <style>
    body {
        color: #333;
        background-color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
