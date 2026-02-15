"""
LLM prompt templates for codebase analysis.
"""

def get_explanation_prompt(context: str) -> str:
    """
    Generate a prompt for explaining code.
    """
    return f"""You are an expert software engineer and code analyst. 
Your task is to answer questions about the following codebase based ONLY on the provided context.

Context:
{context}

Please provide clear, concise, and accurate explanations. If the context doesn't contain enough information to answer the question, please state that clearly.
"""
