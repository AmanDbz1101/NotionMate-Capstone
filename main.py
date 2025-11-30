import streamlit as st 
import os
import tempfile
import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Project imports
from main_chat.prompt import call_prompt
from notion_agent.agent import create_note_from_history
from notion_agent.tools.notion_page_info_retriever import get_notion_pages

load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"

DB_CHROMA_PATH = "vector_store/chroma_index"

@st.cache_resource
def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs={"local_files_only": False})
    vector_store = Chroma(persist_directory="vector_store/chroma_index", embedding_function=embedding_model)
    return vector_store


def format_docs(retrieved_docs):
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text

def format_chat_history(messages, max_messages=6):
    """Format recent messages from Streamlit's session state into conversation history string."""
    recent = messages[-max_messages*2:] if messages else []
    formatted = []
    for msg in recent:
        formatted.append(f"[{msg['role']}] {msg['content']}")
    return "\n".join(formatted)

def get_full_chat_history(messages):
    """Get the complete chat history as a formatted string."""
    if not messages:
        return ""
    
    formatted = []
    for msg in messages:
        if msg['role'] != 'system':
            formatted.append(f"[{msg['role']}] {msg['content']}")
    return "\n".join(formatted)


def get_notion_pages_sync():
    """Get list of Notion pages synchronously for Streamlit."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pages = loop.run_until_complete(get_notion_pages())
        loop.close()
        return pages
    except Exception as e:
        return []


def write_note_to_notion(messages, page_id: str = None):
    """Create note from chat history and write directly to Notion."""
    chat_history = get_full_chat_history(messages)
    if not chat_history:
        return "❌ No chat history available to create a note."
    
    try:
        result = create_note_from_history(chat_history, notion_page_id=page_id)
        
        if not result["success"]:
            return f"❌ Error: {result['error']}"
        
        if result["notion_write_success"]:
            page_id_clean = result['notion_page_id'].replace('-', '')
            notion_url = f"https://notion.so/{page_id_clean}"
            return f"✅ Note added to **{result['notion_page_title']}**!\n\n🔗 [Open in Notion]({notion_url})"
        else:
            return f"❌ Notion write failed: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def process_pdf_file(pdf_file):
    """Process a single PDF file and return its documents."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_file.getvalue())
        temp_path = temp_file.name
    
    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    os.unlink(temp_path)
    
    return documents

def split_documents(documents):
    """Split documents into chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    split_docs = text_splitter.split_documents(documents)
    return split_docs

def update_vector_store(documents, vector_store):
    """Add new documents to the existing vector store."""
    split_docs = split_documents(documents)
    vector_store.add_documents(split_docs)
    vector_store.persist()
    return len(split_docs)


def main():
    st.title("NotionMate Capstone")

    # session messages for UI
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Fetch Notion pages automatically on app start
    if 'notion_pages' not in st.session_state:
        with st.spinner("Loading Notion pages..."):
            st.session_state.notion_pages = get_notion_pages_sync()
    
    # Use a unique key for the file uploader that can be reset
    file_uploader_key = "pdf_uploader"
    if 'file_uploader_key' in st.session_state:
        file_uploader_key = st.session_state.file_uploader_key
    
    # Add the file uploader to the sidebar
    with st.sidebar:
        st.header("Add Documents")
        st.markdown("Upload PDFs to enhance the chatbot's knowledge")
        uploaded_file = st.file_uploader("Upload a PDF file", 
                                        type="pdf",
                                        key=file_uploader_key,
                                        help="Files will be processed and added to the knowledge base")
        
        # Add some info about supported formats
        st.caption("Supported format: PDF")
        
        # Add some spacing
        st.markdown("---")
        
        # Add info about the current knowledge base
        st.markdown("### About")
        st.markdown("This chatbot uses RAG (Retrieval Augmented Generation) to answer questions based on the uploaded PDFs.")
        # st.markdown("### Pre-loaded information about gastritis healing.")
        st.markdown(
            '<p style="color: yellow;">Pre-loaded information about gastritis healing.</p>',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown("### Write to Notion")
        
        # Show dropdown if pages are available
        if 'notion_pages' in st.session_state and st.session_state.notion_pages:
            page_titles = [p['title'] for p in st.session_state.notion_pages]
            selected_page = st.selectbox(
                "Select Notion Page",
                options=page_titles,
                help="Choose which page to add the note to"
            )
            
            # Get the selected page ID
            selected_page_id = next(
                (p['id'] for p in st.session_state.notion_pages if p['title'] == selected_page),
                None
            )
            
            if st.button("Write to Notion", type="primary"):
                with st.spinner(f"📝 Creating summary and writing to '{selected_page}'..."):
                    notion_response = write_note_to_notion(st.session_state.messages, selected_page_id)
                    st.markdown(notion_response)
        else:
            st.warning("No Notion pages found. Please check your Notion connection.")
        
    # Set up placeholder for status messages
    status_container = st.container()
    
    # Process uploaded PDF file if provided
    if uploaded_file:
        with status_container:
            with st.spinner("Processing PDF file..."):
                try:
                    # Load vector store
                    vector_store = load_vector_store()
                    
                    # Process the uploaded file
                    documents = process_pdf_file(uploaded_file)
                    
                    # Update the vector store
                    chunks_added = update_vector_store(documents, vector_store)
                    
                    # Success message
                    st.success(f"Successfully processed PDF: {uploaded_file.name}. Added {chunks_added} chunks to the knowledge base.")
                    
                    # Reset the file uploader by changing its key
                    st.session_state.file_uploader_key = f"pdf_uploader_{hash(uploaded_file.name)}"
                    
                    # Add a system message
                    system_msg = f"PDF '{uploaded_file.name}' has been added to the knowledge base. You can now ask questions about it."
                    st.session_state.messages.append({"role": "system", "content": system_msg})
                
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
    
    # Create a container for messages with scrolling
    messages_container = st.container()
    
    # Display chat messages in a scrollable container
    with messages_container:
        st.markdown('<div class="chat-message-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            st.chat_message(message['role']).markdown(message['content'])
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Chat input at the bottom
    input = st.chat_input("Ask a question about ...")
    try:
        vector_store = load_vector_store()
        if vector_store is None:
            st.error("Vector store not found. Please ensure it is loaded correctly.")
            return
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return 
    if input:
        st.session_state.messages.append({"role": "user", "content": input})
        st.chat_message("user").markdown(input)
        # persist user message


        # llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        llm = ChatGroq(model="openai/gpt-oss-120b")

        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
        parser = StrOutputParser()

        # Format conversation history from Streamlit messages
        chat_history = format_chat_history(st.session_state.messages)
        
        parallel_chain = RunnableParallel({
            # 'context': retriever | RunnableLambda(format_docs),
            'context': RunnableLambda(lambda x: retriever.invoke(x["input"])) | RunnableLambda(format_docs),
            'conversation_history': RunnableLambda(lambda _: chat_history),
            'input': RunnablePassthrough()
        })
        prompt = call_prompt()
        main_chain = parallel_chain | prompt | llm | parser

        response = main_chain.invoke({'input': input})

        
        
        
        # Here you would call your chatbot function to get the response
        # response = "This is a placeholder response from the chatbot."
        st.chat_message("assistant").markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        
        
if __name__ == "__main__":
    main()