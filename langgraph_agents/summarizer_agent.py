from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL

class SummarizerAgent:
    """Agent for generating document summaries using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def summarize(self, text: str) -> str:
        """
        Generate a comprehensive summary of the document
        Returns formatted summary
        """
        if not text or not text.strip():
            return "No text content provided for summarization."
            
        try:
            # Break text into chunks if it's too long (GPT-4 context limit)
            max_chunk_length = 24000  # GPT-4's approximate token limit (~75% of max to leave room for response)
            if len(text) > max_chunk_length:
                text = text[:max_chunk_length] + "\n[Text truncated due to length...]"
            
            # Construct prompt
            prompt = f"""Please provide a comprehensive summary of the following document. 
            Include the main topics, key points, and important conclusions.
            Format the summary with clear sections and bullet points where appropriate.
            
            Document:
            {text}
            
            Instructions:
            1. Start with a brief overview
            2. List main topics using bullet points
            3. Highlight key findings or conclusions
            4. Use clear formatting for readability
            
            Summary:"""
            
            # Generate summary using OpenAI
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates comprehensive document summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                
                if not response or not response.choices:
                    return "Failed to generate summary. The model returned an empty response."
                    
                return response.choices[0].message.content
                
            except Exception as model_error:
                return f"Model error: {str(model_error)}"
            
        except Exception as e:
            return f"Error preparing summary: {str(e)}"
