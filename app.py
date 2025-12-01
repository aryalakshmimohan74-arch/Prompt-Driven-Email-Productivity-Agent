from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import Database
from llm_service import LLMService
from email_processor import EmailProcessor
from models import Email, Prompt, Draft, ChatRequest, ProcessEmailsRequest
from typing import List, Dict
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Email Productivity Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
llm = LLMService()
processor = EmailProcessor(db, llm)

@app.get("/")
def read_root():
    return {"message": "Email Productivity Agent API is running"}

# Email endpoints
@app.get("/emails")
def get_emails() -> List[Dict]:
    """Get all emails"""
    return db.get_all_emails()

@app.get("/emails/{email_id}")
def get_email(email_id: int) -> Dict:
    """Get a specific email"""
    email = db.get_email_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@app.post("/emails/load-mock")
def load_mock_inbox(mock_data: List[Dict]) -> Dict:
    """Load mock inbox data"""
    try:
        results = processor.load_mock_inbox(mock_data)
        return {
            "status": "success",
            "message": f"Loaded {len(results)} emails",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/process")
def process_emails(request: ProcessEmailsRequest) -> Dict:
    """Process a batch of emails"""
    try:
        results = processor.process_emails_batch(request.emails)
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/emails")
def delete_all_emails() -> Dict:
    """Delete all emails"""
    db.delete_all_emails()
    return {"status": "success", "message": "All emails deleted"}

# Prompt endpoints
@app.get("/prompts")
def get_prompts() -> List[Dict]:
    """Get all prompts"""
    return db.get_all_prompts()

@app.get("/prompts/{name}")
def get_prompt(name: str) -> Dict:
    """Get a specific prompt"""
    prompt = db.get_prompt(name)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@app.post("/prompts")
def create_or_update_prompt(prompt: Prompt) -> Dict:
    """Create or update a prompt"""
    db.upsert_prompt(prompt.name, prompt.content, prompt.description)
    return {"status": "success", "message": f"Prompt '{prompt.name}' saved"}

@app.post("/prompts/load-defaults")
def load_default_prompts(prompts: List[Dict]) -> Dict:
    """Load default prompts"""
    for prompt in prompts:
        db.upsert_prompt(
            name=prompt['name'],
            content=prompt['content'],
            description=prompt.get('description', '')
        )
    return {"status": "success", "message": f"Loaded {len(prompts)} default prompts"}

# Draft endpoints
@app.get("/drafts")
def get_drafts() -> List[Dict]:
    """Get all drafts"""
    return db.get_all_drafts()

@app.get("/drafts/{draft_id}")
def get_draft(draft_id: int) -> Dict:
    """Get a specific draft"""
    draft = db.get_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@app.post("/drafts")
def create_draft(draft: Draft) -> Dict:
    """Create a new draft"""
    draft_id = db.insert_draft(
        email_id=draft.email_id,
        subject=draft.subject,
        body=draft.body,
        metadata=draft.metadata
    )
    return {
        "status": "success",
        "draft_id": draft_id,
        "message": "Draft created"
    }

@app.delete("/drafts/{draft_id}")
def delete_draft(draft_id: int) -> Dict:
    """Delete a draft"""
    db.delete_draft(draft_id)
    return {"status": "success", "message": "Draft deleted"}

# Agent/Chat endpoints
@app.post("/agent/chat")
def chat_with_agent(request: ChatRequest) -> Dict:
    """Chat with the email agent"""
    try:
        email_content = None
        if request.email_id:
            email = db.get_email_by_id(request.email_id)
            if email:
                email_content = f"Subject: {email['subject']}\nFrom: {email['sender']}\nBody: {email['body']}"
        
        all_emails = None
        if not request.email_id:
            emails = db.get_all_emails()
            all_emails = "\n\n".join([
                f"[{e['id']}] From: {e['sender']}\nSubject: {e['subject']}\nCategory: {e.get('category', 'N/A')}"
                for e in emails[:10]  # Limit to 10 emails
            ])
        
        response = llm.chat_about_email(
            query=request.query,
            email_content=email_content,
            all_emails=all_emails
        )
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/draft-reply/{email_id}")
def draft_reply(email_id: int, context: str = "") -> Dict:
    """Draft a reply to an email"""
    try:
        email = db.get_email_by_id(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        reply_prompt = db.get_prompt("auto_reply")
        if not reply_prompt:
            raise HTTPException(status_code=404, detail="Reply prompt not found")
        
        draft = llm.draft_reply(
            email_body=email['body'],
            email_subject=email['subject'],
            reply_prompt=reply_prompt['content'],
            user_context=context
        )
        
        # Save draft
        draft_id = db.insert_draft(
            email_id=email_id,
            subject=draft['subject'],
            body=draft['body'],
            metadata=json.dumps({"type": "reply", "original_email_id": email_id})
        )
        
        return {
            "status": "success",
            "draft_id": draft_id,
            "draft": draft
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/generate-email")
def generate_email(instruction: str, context: str = "") -> Dict:
    """Generate a new email"""
    try:
        email = llm.generate_new_email(instruction, context)
        
        # Save as draft
        draft_id = db.insert_draft(
            email_id=None,
            subject=email['subject'],
            body=email['body'],
            metadata=json.dumps({"type": "new", "instruction": instruction})
        )
        
        return {
            "status": "success",
            "draft_id": draft_id,
            "email": email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
