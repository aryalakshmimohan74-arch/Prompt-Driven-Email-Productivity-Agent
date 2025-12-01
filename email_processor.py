from database import Database
from llm_service import LLMService
from models import Email
from typing import List, Dict
import json

class EmailProcessor:
    def __init__(self, db: Database, llm: LLMService):
        self.db = db
        self.llm = llm
    
    def process_single_email(self, email: Email) -> Dict:
        """Process a single email: categorize and extract action items"""
        # Get prompts from database
        cat_prompt = self.db.get_prompt("categorization")
        action_prompt = self.db.get_prompt("action_items")
        
        if not cat_prompt or not action_prompt:
            return {
                "error": "Prompts not found. Please configure prompts first."
            }
        
        # Categorize email
        category = self.llm.categorize_email(
            email.body,
            email.subject,
            cat_prompt['content']
        )
        
        # Extract action items
        action_items = self.llm.extract_action_items(
            email.body,
            email.subject,
            action_prompt['content']
        )
        
        return {
            "category": category,
            "action_items": action_items
        }
    
    def process_emails_batch(self, emails: List[Email]) -> List[Dict]:
        """Process multiple emails"""
        results = []
        
        for email in emails:
            try:
                result = self.process_single_email(email)
                
                # Insert or update email in database
                email_id = self.db.insert_email(
                    sender=email.sender,
                    subject=email.subject,
                    body=email.body,
                    timestamp=email.timestamp,
                    category=result.get("category"),
                    action_items=result.get("action_items")
                )
                
                results.append({
                    "email_id": email_id,
                    "status": "success",
                    **result
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def load_mock_inbox(self, mock_data: List[Dict]) -> List[Dict]:
        """Load mock inbox data"""
        emails = [Email(**email_data) for email_data in mock_data]
        return self.process_emails_batch(emails)
