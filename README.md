# PDF Smart Summarizer & Q&A Assistant

A Streamlit-based intelligent PDF assistant that can summarize and answer questions about any PDF document, handling both text-based and image-based (scanned) PDFs using OCR.

## Features

- 📚 Process any PDF document (text or scanned)
- 🔍 OCR support for image-based PDFs using EasyOCR
- 🤖 Intelligent agent-based architecture using LangGraph
- 💡 Smart document processing with Gemini AI
- 🔎 RAG (Retrieval Augmented Generation) for accurate answers
- 📊 Vector storage using FAISS for efficient retrieval
- 🌐 Clean, modern Streamlit UI

## Tech Stack

- **LLM**: OpenAI GPT-4
- **PDF Parsing**: PyMuPDF
- **OCR**: EasyOCR
- **Vector DB**: FAISS
- **Agent Orchestration**: LangGraph
- **UI**: Streamlit
- **Embeddings**: OpenAI text-embedding-3-large

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-summarizer-rag
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env and add your OpenAI API key
# Replace 'your-api-key-here' with your actual OpenAI API key
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser at `http://localhost:8501`

3. Upload a PDF file

4. Use the interface to:
   - Generate document summaries
   - Ask questions about the document
   - Download summaries

## Project Structure

```
pdf_summarizer_rag/
│
├── app.py                        # Streamlit UI entry point
├── main_controller.py           # LangGraph controller
├── requirements.txt            # Dependencies
├── config.py                   # Configuration
│
├── langgraph_agents/          # Modular agents
│   ├── pdf_parser_agent.py
│   ├── ocr_agent.py
│   ├── collector_agent.py
│   ├── embedding_agent.py
│   ├── vector_store_agent.py
│   ├── rag_agent.py
│   ├── summarizer_agent.py
│   └── router_agent.py
│
├── vector_store/             # FAISS storage
├── utils/                   # Helper utilities
└── outputs/                # Generated outputs
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
