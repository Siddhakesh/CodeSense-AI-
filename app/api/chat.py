"""
API endpoint for conversational Q&A about repositories.
"""
from fastapi import APIRouter

router = APIRouter()


from pydantic import BaseModel
from ..llm.answerer import answer_question
from ..llm.prompts import get_explanation_prompt

class ChatRequest(BaseModel):
    repo_id: str
    question: str
    context: str = "" # Optional client-provided context, or we load from server state

@router.post("/chat")
async def chat_with_repo(request: ChatRequest):
    """
    Answer questions about a repository using LLM.
    """
    # In a real app, we would load the repo index/context from a database using repo_id
    # For MVP, we'll assume the client might pass some context or we just use the question
    # with a generic prompt if no context management is implemented yet.
    
    # Construct prompt
    prompt_context = request.context
    if not prompt_context:
        # Try to read some summary if available or just generic
        prompt_context = f"Repository: {request.repo_id}"
        
    prompt = get_explanation_prompt(prompt_context)
    
    answer = await answer_question(request.question, prompt)
    
    return {"answer": answer}
