"""
LLM integration for answering questions about codebases.
"""

import os
import google.generativeai as genai

# Configure API key
def _configure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)

async def answer_question(question: str, context: str) -> str:
    """
    Answer a question about a codebase using LLM.
    
    Args:
        question: User's question
        context: Context string (e.g. from prompts.py)
        
    Returns:
        LLM-generated answer
    """
    try:
        _configure_genai()
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Combine context and question
        full_prompt = f"{context}\n\nQuestion: {question}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"
