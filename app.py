import streamlit as st
import time
from pathlib import Path
from main_controller import PDFProcessor
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS

# Set page configuration with custom theme
st.set_page_config(
    page_title="PDF Smart Summarizer & Q&A Assistant",
    page_icon="Logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with modern styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main {
            padding: 0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 0 0 30px 30px;
            margin: -1rem -1rem 2rem -1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            color: white;
        }
        
        .header-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header-subtitle {
            font-size: 1.2rem;
            font-weight: 300;
            opacity: 0.9;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
        }
        
        /* Card styling */
        .feature-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            margin-bottom: 2rem;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .feature-card h3 {
            color: #333;
            font-weight: 600;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 500;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            width: 100%;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* File uploader styling */
        .stFileUploader > div > div {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border: 2px dashed rgba(255,255,255,0.3);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            color: white;
            font-weight: 500;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .sidebar-content {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
        }
        
        /* Metrics styling */
        .metric-container {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            color: #666;
            font-weight: 500;
        }
        
        /* Status styling */
        .status-container {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 15px;
            padding: 1rem;
            color: white;
            font-weight: 500;
        }
        
        /* Chat bubble styling */
        .chat-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 20px;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }
        
        .answer-bubble {
            background: white;
            color: #333;
            padding: 1.5rem;
            border-radius: 20px;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 15px;
            border: 2px solid #e0e6ed;
            padding: 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Animation for loading */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        /* Success message styling */
        .success-message {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: white;
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        /* Error message styling */
        .error-message {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #d63384;
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        /* Hide default streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        }
    </style>
""", unsafe_allow_html=True)

def main():
    # Enhanced header with modern gradient
    st.markdown("""
        <div class="header-container">
            <div class="header-title">📚 PDF Smart Assistant</div>
            <div class="header-subtitle">
                Transform your documents into interactive knowledge with AI-powered summaries and intelligent Q&A. 
                Experience the future of document analysis.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced sidebar with glassmorphism effect
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-content">
                <h2 style='text-align: center; margin-bottom: 1rem;'>🛠️ Control Panel</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Vector Database", type="secondary"):
            processor = PDFProcessor()
            processor.clear_vector_store()
            st.markdown('<div class="success-message">✨ Vector database cleared successfully!</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="sidebar-content">
                <h3>📊 System Stats</h3>
                <div style='margin: 1rem 0;'>
                    <div style='background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 10px; margin: 0.5rem 0;'>
                        📄 Supported: PDF
                    </div>
                    <div style='background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 10px; margin: 0.5rem 0;'>
                        📏 Max Size: {}MB
                    </div>
                    <div style='background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 10px; margin: 0.5rem 0;'>
                        👁️ OCR: Enabled
                    </div>
                </div>
            </div>
        """.format(MAX_FILE_SIZE//1024//1024), unsafe_allow_html=True)

    # File upload section with enhanced styling
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "PDF Document",
            type=SUPPORTED_FORMATS,
            help=f"Drag and drop or click to upload • Max size: {MAX_FILE_SIZE//1024//1024}MB",
            label_visibility="collapsed"
        )

    if uploaded_file:
        # Check file size
        if uploaded_file.size > MAX_FILE_SIZE:
            st.markdown('<div class="error-message">📢 File size exceeds the limit!</div>', unsafe_allow_html=True)
            return

        # Enhanced document info with beautiful metrics
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{uploaded_file.size/1024/1024:.1f}</div>
                    <div class="metric-label">MB File Size</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">PDF</div>
                    <div class="metric-label">Document Type</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">✅</div>
                    <div class="metric-label">Ready to Process</div>
                </div>
            """, unsafe_allow_html=True)

        # Initialize processor
        processor = PDFProcessor()

        with st.status("🔄 Processing document...", expanded=True) as status:
            st.write("🚀 Initializing document processing...")
            success, error_msg = processor.process_pdf(uploaded_file)
            
            if success:
                status.update(label="✅ Document processed successfully!", state="complete", expanded=False)
                st.markdown('<div class="success-message">🎉 Your document is ready for analysis!</div>', unsafe_allow_html=True)
            else:
                if "encrypted" in error_msg.lower():
                    st.markdown('<div class="error-message">🔒 This PDF is encrypted. Please provide an unencrypted file.</div>', unsafe_allow_html=True)
                elif "corrupted" in error_msg.lower():
                    st.markdown('<div class="error-message">❌ PDF appears corrupted. Please verify and try again.</div>', unsafe_allow_html=True)
                elif "empty" in error_msg.lower() or "no text content" in error_msg.lower():
                    st.markdown('<div class="error-message">📝 No readable content found. Ensure PDF contains text.</div>', unsafe_allow_html=True)
                elif "ocr" in error_msg.lower():
                    st.markdown('<div class="error-message">👁️ OCR processing failed. Image text could not be extracted.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-message">⚠️ {error_msg}</div>', unsafe_allow_html=True)
                return

        # Enhanced feature cards with modern design
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📝</div>
                    <h3>Intelligent Summary</h3>
                    <p style='color: #666; line-height: 1.6; margin-bottom: 2rem;'>
                        Generate comprehensive, AI-powered summaries that capture the essence of your document.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎯 Generate Smart Summary", key="generate_summary"):
                with st.status("🧠 Analyzing document...", expanded=True) as status:
                    st.write("✨ Creating intelligent summary...")
                    summary = processor.generate_summary()
                    status.update(label="🎉 Summary generated!", state="complete", expanded=False)
                    
                    st.markdown("""
                        <div class="answer-bubble">
                            <h4 style='margin-bottom: 1rem; color: #667eea;'>📋 Document Summary</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(summary)
                    
                    # Enhanced download button
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        st.download_button(
                            "📥 Download Summary",
                            summary,
                            file_name=f"{uploaded_file.name}_summary.pdf",
                            mime="pdf",
                            help="Save summary as text file"
                        )
        
        with col2:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3>Interactive Q&A</h3>
                    <p style='color: #666; line-height: 1.6; margin-bottom: 2rem;'>
                        Ask any question about your document and get instant, contextually accurate answers.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Enhanced question input
            question = st.text_input(
                "🔍 What would you like to know?",
                placeholder="e.g., What are the key findings in this document?",
                help="Ask anything about your document content"
            )
            
            if question:
                with st.status("🤔 Searching for answers...", expanded=True) as status:
                    st.write("🔍 Analyzing document context...")
                    answer = processor.answer_question(question)
                    status.update(label="💡 Answer found!", state="complete", expanded=False)
                    
                    # Question bubble
                    st.markdown(f"""
                        <div class="chat-bubble">
                            <strong>❓ Your Question:</strong><br>
                            {question}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Answer bubble
                    st.markdown(f"""
                        <div class="answer-bubble">
                            <h4 style='margin-bottom: 1rem; color: #667eea;'>💡 AI Answer:</h4>
                            {answer}
                        </div>
                    """, unsafe_allow_html=True)

    else:
        # Welcome message when no file is uploaded
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div class="feature-card" style='text-align: center;'>
                    <div class="feature-icon">🚀</div>
                    <h3>Welcome to PDF Smart Assistant</h3>
                    <p style='color: #666; line-height: 1.6;'>
                        Upload your PDF document above to start experiencing the magic of AI-powered document analysis.
                        Get instant summaries and ask questions about your content!
                    </p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
